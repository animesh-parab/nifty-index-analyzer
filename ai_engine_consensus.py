"""
ai_engine_consensus.py
Dual-AI Consensus Prediction Engine
Uses both Groq (Llama 3.3 70B) and Gemini (1.5 Flash) for validated predictions
"""

import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from groq import Groq
from google import genai
from config import GROQ_API_KEY, GROQ_MODEL, GEMINI_API_KEY
from datetime import datetime
import pytz
from api_rate_monitor import record_api_call

IST = pytz.timezone("Asia/Kolkata")


def _build_analysis_prompt(
    price_data: dict,
    indicator_summary: dict,
    oi_data: dict,
    vix_data: dict,
    news_sentiment: dict,
    greeks: dict,
    global_cues: dict,
    patterns: dict,
) -> str:
    """Build comprehensive prompt for AI analysis"""
    
    now = datetime.now(IST).strftime("%d %b %Y %H:%M IST")

    prompt = f"""You are an expert Indian stock market analyst specializing in Nifty 50 options trading. 
Analyze the following live market data and provide a precise short-term prediction.

=== TIMESTAMP: {now} ===

=== NIFTY LIVE PRICE ===
Current Price: {price_data.get('price', 'N/A')}
Open: {price_data.get('open', 'N/A')}
High: {price_data.get('high', 'N/A')}
Low: {price_data.get('low', 'N/A')}
Change: {price_data.get('change', 'N/A')} ({price_data.get('pct_change', 'N/A')}%)

=== INDIA VIX ===
VIX: {vix_data.get('vix', 'N/A')}
Change: {vix_data.get('change', 'N/A')} ({vix_data.get('pct_change', 'N/A')}%)
Interpretation: {"LOW VIX - Options cheap" if vix_data.get('vix', 15) < 13 else "HIGH VIX - Options expensive" if vix_data.get('vix', 15) > 20 else "NORMAL VIX"}

=== TECHNICAL INDICATORS ===
{json.dumps(indicator_summary, indent=2)}

=== CANDLESTICK PATTERNS ===
{json.dumps(patterns, indent=2) if patterns else "No significant patterns"}

=== OPTIONS CHAIN ===
PCR: {oi_data.get('pcr', 'N/A')} - {"BULLISH (>1.2)" if oi_data.get('pcr', 1) > 1.2 else "BEARISH (<0.8)" if oi_data.get('pcr', 1) < 0.8 else "NEUTRAL"}
Max Pain: {oi_data.get('max_pain', 'N/A')}
Resistance: {oi_data.get('resistance', 'N/A')}
Support: {oi_data.get('support', 'N/A')}

=== NEWS SENTIMENT ===
Overall: {news_sentiment.get('overall', 'N/A')}
Score: {news_sentiment.get('score', 'N/A')} (-1=bearish, +1=bullish)

=== GLOBAL CUES ===
{chr(10).join([f"{k}: {v.get('pct_change', 0):+.2f}%" for k, v in list(global_cues.items())[:5]])}

=== RESPOND IN THIS EXACT JSON FORMAT ===
{{
  "direction": "BULLISH" or "BEARISH" or "SIDEWAYS",
  "confidence": <integer 0-100>,
  "strength": "WEAK" or "MODERATE" or "STRONG",
  "price_targets": {{
    "5min": {{"high": <price>, "low": <price>, "most_likely": <price>}},
    "15min": {{"high": <price>, "low": <price>, "most_likely": <price>}},
    "30min": {{"high": <price>, "low": <price>, "most_likely": <price>}}
  }},
  "top_3_reasons": [
    "<Reason 1>",
    "<Reason 2>",
    "<Reason 3>"
  ],
  "one_line_summary": "<single sentence summary>"
}}

Be precise. Use actual Nifty price numbers. Respond with ONLY valid JSON."""

    return prompt


def _call_groq_api(prompt: str) -> dict:
    """Call Groq API (Llama 3.3 70B)"""
    try:
        if not GROQ_API_KEY:
            return {"error": "GROQ_API_KEY not set", "model": "groq"}
        
        client = Groq(api_key=GROQ_API_KEY)
        
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional Nifty 50 trader. Respond with valid JSON only."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1500,
        )
        
        # Record API call
        tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0
        record_api_call("groq", "chat.completions", tokens_used)
        
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        
        prediction = json.loads(raw)
        prediction["model"] = "groq"
        prediction["model_name"] = "Llama 3.3 70B"
        return prediction
        
    except json.JSONDecodeError as e:
        return {
            "error": f"JSON parse error: {e}",
            "model": "groq",
            "direction": "NEUTRAL",
            "confidence": 0
        }
    except Exception as e:
        return {
            "error": str(e),
            "model": "groq",
            "direction": "NEUTRAL",
            "confidence": 0
        }


def _call_gemini_api(prompt: str) -> dict:
    """Call Gemini API (Gemini 2.5 Flash) using new google-genai package"""
    try:
        if not GEMINI_API_KEY:
            return {"error": "GEMINI_API_KEY not set", "model": "gemini"}
        
        # Initialize client with new API
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Use the latest flash model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                'temperature': 0.2,
                'max_output_tokens': 1500,
                'response_mime_type': 'application/json',  # Force JSON response
            }
        )
        
        # Record API call
        record_api_call("gemini", "generate_content", 0)
        
        raw = response.text.strip()
        
        # The response should already be valid JSON with response_mime_type set
        prediction = json.loads(raw)
        prediction["model"] = "gemini"
        prediction["model_name"] = "Gemini 2.5 Flash"
        return prediction
        
    except json.JSONDecodeError as e:
        # If JSON parsing fails, try to extract JSON from the response
        try:
            if '{' in raw and '}' in raw:
                start = raw.find('{')
                end = raw.rfind('}') + 1
                cleaned = raw[start:end]
                prediction = json.loads(cleaned)
                prediction["model"] = "gemini"
                prediction["model_name"] = "Gemini 2.5 Flash"
                return prediction
        except:
            pass
        
        return {
            "error": f"JSON parse error: {str(e)[:100]}",
            "model": "gemini",
            "direction": "NEUTRAL",
            "confidence": 0
        }
    except Exception as e:
        return {
            "error": str(e)[:200],
            "model": "gemini",
            "direction": "NEUTRAL",
            "confidence": 0
        }


def _calculate_consensus(groq_pred: dict, gemini_pred: dict) -> dict:
    """Calculate consensus between two AI predictions"""
    
    groq_dir = groq_pred.get("direction", "NEUTRAL")
    gemini_dir = gemini_pred.get("direction", "NEUTRAL")
    groq_conf = groq_pred.get("confidence", 0)
    gemini_conf = gemini_pred.get("confidence", 0)
    
    # Check for errors
    groq_error = "error" in groq_pred
    gemini_error = "error" in gemini_pred
    
    if groq_error and gemini_error:
        # Both failed - use rule-based
        return {
            "consensus": "FAILED",
            "direction": "NEUTRAL",
            "confidence": 0,
            "agreement": "NONE",
            "groq_prediction": groq_pred,
            "gemini_prediction": gemini_pred,
            "use_fallback": True
        }
    
    if groq_error:
        # Only Groq failed - use Gemini
        return {
            "consensus": "GEMINI_ONLY",
            "direction": gemini_dir,
            "confidence": gemini_conf,
            "agreement": "SINGLE",
            "groq_prediction": groq_pred,
            "gemini_prediction": gemini_pred,
            "primary_model": "gemini"
        }
    
    if gemini_error:
        # Only Gemini failed - use Groq
        return {
            "consensus": "GROQ_ONLY",
            "direction": groq_dir,
            "confidence": groq_conf,
            "agreement": "SINGLE",
            "groq_prediction": groq_pred,
            "gemini_prediction": gemini_pred,
            "primary_model": "groq"
        }
    
    # Both succeeded - calculate consensus
    if groq_dir == gemini_dir:
        # Perfect agreement
        consensus = "STRONG"
        final_direction = groq_dir
        final_confidence = min(95, int((groq_conf + gemini_conf) / 2 + 10))
        agreement = "FULL"
        
    elif (groq_dir == "SIDEWAYS" or gemini_dir == "SIDEWAYS") and groq_dir != gemini_dir:
        # Partial agreement (one says sideways)
        consensus = "MODERATE"
        # Use the non-sideways direction
        final_direction = groq_dir if groq_dir != "SIDEWAYS" else gemini_dir
        final_confidence = int((groq_conf + gemini_conf) / 2 - 5)
        agreement = "PARTIAL"
        
    else:
        # Complete disagreement (BULLISH vs BEARISH)
        consensus = "WEAK"
        # Use higher confidence prediction
        if groq_conf > gemini_conf:
            final_direction = groq_dir
            final_confidence = int(groq_conf - 20)
        else:
            final_direction = gemini_dir
            final_confidence = int(gemini_conf - 20)
        agreement = "CONFLICTING"
    
    # Merge price targets (average if both available)
    price_targets = {}
    groq_targets = groq_pred.get("price_targets", {})
    gemini_targets = gemini_pred.get("price_targets", {})
    
    for timeframe in ["5min", "15min", "30min"]:
        if timeframe in groq_targets and timeframe in gemini_targets:
            gt = groq_targets[timeframe]
            gm = gemini_targets[timeframe]
            price_targets[timeframe] = {
                "high": int((gt.get("high", 0) + gm.get("high", 0)) / 2),
                "low": int((gt.get("low", 0) + gm.get("low", 0)) / 2),
                "most_likely": int((gt.get("most_likely", 0) + gm.get("most_likely", 0)) / 2)
            }
        elif timeframe in groq_targets:
            price_targets[timeframe] = groq_targets[timeframe]
        elif timeframe in gemini_targets:
            price_targets[timeframe] = gemini_targets[timeframe]
    
    # Merge reasons
    groq_reasons = groq_pred.get("top_3_reasons", [])
    gemini_reasons = gemini_pred.get("top_3_reasons", [])
    
    # Combine and deduplicate reasons
    all_reasons = []
    for reason in groq_reasons + gemini_reasons:
        if reason not in all_reasons:
            all_reasons.append(reason)
    
    return {
        "consensus": consensus,
        "direction": final_direction,
        "confidence": final_confidence,
        "agreement": agreement,
        "price_targets": price_targets,
        "top_3_reasons": all_reasons[:3],
        "groq_prediction": groq_pred,
        "gemini_prediction": gemini_pred,
        "groq_direction": groq_dir,
        "gemini_direction": gemini_dir,
        "groq_confidence": groq_conf,
        "gemini_confidence": gemini_conf,
        "one_line_summary": f"{consensus} consensus: {final_direction} ({final_confidence}%)"
    }


def get_consensus_prediction(
    price_data: dict,
    indicator_summary: dict,
    oi_data: dict,
    vix_data: dict,
    news_sentiment: dict,
    greeks: dict,
    global_cues: dict,
    patterns: dict,
) -> dict:
    """
    Get consensus prediction from both Groq and Gemini
    Calls both APIs in parallel for speed
    """
    
    # Build prompt
    prompt = _build_analysis_prompt(
        price_data, indicator_summary, oi_data,
        vix_data, news_sentiment, greeks, global_cues, patterns
    )
    
    # Call both APIs in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as executor:
        groq_future = executor.submit(_call_groq_api, prompt)
        gemini_future = executor.submit(_call_gemini_api, prompt)
        
        groq_pred = groq_future.result()
        gemini_pred = gemini_future.result()
    
    # Calculate consensus
    consensus = _calculate_consensus(groq_pred, gemini_pred)
    
    # Add metadata
    consensus["generated_at"] = datetime.now(IST).strftime("%H:%M:%S IST")
    consensus["model_used"] = "Dual-AI Consensus (Groq + Gemini)"
    
    return consensus


def get_rule_based_prediction(indicator_summary: dict, oi_data: dict, vix_data: dict, news: dict) -> dict:
    """
    Fallback rule-based prediction when both AIs fail
    """
    score = 0
    reasons = []

    # RSI
    rsi = indicator_summary.get("RSI", {})
    if rsi.get("signal") in ["BULLISH", "OVERSOLD"]:
        score += 1
        reasons.append(f"RSI {rsi.get('signal')}")
    elif rsi.get("signal") in ["BEARISH", "OVERBOUGHT"]:
        score -= 1
        reasons.append(f"RSI {rsi.get('signal')}")

    # MACD
    macd = indicator_summary.get("MACD", {})
    if "BULLISH" in macd.get("signal", ""):
        score += 2 if "STRONG" in macd.get("signal", "") else 1
        reasons.append(f"MACD {macd.get('signal')}")
    elif "BEARISH" in macd.get("signal", ""):
        score -= 2 if "STRONG" in macd.get("signal", "") else 1
        reasons.append(f"MACD {macd.get('signal')}")

    # EMA
    ema = indicator_summary.get("EMA_Trend", {})
    if "UPTREND" in ema.get("signal", ""):
        score += 2 if "STRONG" in ema.get("signal", "") else 1
    elif "DOWNTREND" in ema.get("signal", ""):
        score -= 2 if "STRONG" in ema.get("signal", "") else 1

    # PCR
    pcr = oi_data.get("pcr", 1)
    if pcr > 1.2:
        score += 1
        reasons.append(f"PCR {pcr:.2f} Bullish")
    elif pcr < 0.8:
        score -= 1
        reasons.append(f"PCR {pcr:.2f} Bearish")

    # News
    news_score = news.get("score", 0)
    if news_score > 0.2:
        score += 1
    elif news_score < -0.2:
        score -= 1

    # Determine direction
    if score >= 3:
        direction = "BULLISH"
        confidence = min(80, 50 + score * 5)
        strength = "STRONG"
    elif score >= 1:
        direction = "BULLISH"
        confidence = min(65, 45 + score * 5)
        strength = "MODERATE"
    elif score <= -3:
        direction = "BEARISH"
        confidence = min(80, 50 + abs(score) * 5)
        strength = "STRONG"
    elif score <= -1:
        direction = "BEARISH"
        confidence = min(65, 45 + abs(score) * 5)
        strength = "MODERATE"
    else:
        direction = "SIDEWAYS"
        confidence = 40
        strength = "WEAK"

    return {
        "direction": direction,
        "confidence": confidence,
        "strength": strength,
        "consensus": "RULE_BASED",
        "agreement": "FALLBACK",
        "top_3_reasons": reasons[:3],
        "one_line_summary": f"Rule-based: {direction} ({confidence}%)",
        "model_used": "Rule-based fallback",
        "generated_at": datetime.now(IST).strftime("%H:%M:%S IST"),
    }
