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


def _direction_to_text(direction: int) -> str:
    """Convert numeric direction to text."""
    if direction == 1:
        return "BULLISH"
    elif direction == -1:
        return "BEARISH"
    else:
        return "SIDEWAYS"


def _text_to_direction(text: str) -> int:
    """Convert text direction to numeric."""
    text = text.upper()
    if "BULL" in text:
        return 1
    elif "BEAR" in text:
        return -1
    else:
        return 0


def _extract_xgb_features(indicator_summary: dict, oi_data: dict, 
                          vix_data: dict, global_cues: dict) -> dict:
    """
    Extract raw indicator values for XGBoost from indicator summary.
    
    Args:
        indicator_summary: Dict with indicator signals
        oi_data: Options chain data
        vix_data: VIX data
        global_cues: Global market data
    
    Returns:
        Dict with all XGBoost features
    """
    try:
        now = datetime.now(IST)
        
        # Extract RSI
        rsi = indicator_summary.get("RSI", {}).get("value", 50)
        
        # Extract MACD
        macd_data = indicator_summary.get("MACD", {})
        macd_value = macd_data.get("value", 0)
        macd_signal = macd_value - macd_data.get("histogram", 0)  # Approximate signal
        
        # Extract EMAs
        ema_data = indicator_summary.get("EMA_Trend", {})
        ema_9 = ema_data.get("ema9", 0)
        ema_21 = ema_data.get("ema21", 0)
        ema_50 = ema_data.get("ema50", 0)
        
        # Extract BB position
        bb_data = indicator_summary.get("Bollinger_Bands", {})
        bb_upper = bb_data.get("upper", 0)
        bb_lower = bb_data.get("lower", 0)
        close = bb_data.get("value", 0)
        
        if bb_upper > bb_lower and bb_upper > 0:
            bb_position = (close - bb_lower) / (bb_upper - bb_lower)
        else:
            bb_position = 0.5
        
        # Extract ATR
        atr = indicator_summary.get("ATR", {}).get("value", 0)
        
        # Get US market change (average of major indices)
        us_change = 0
        if global_cues:
            us_indices = ['Dow Futures', 'S&P 500', 'Nasdaq']
            changes = [global_cues.get(idx, {}).get('pct_change', 0) 
                      for idx in us_indices if idx in global_cues]
            if changes:
                us_change = sum(changes) / len(changes)
        
        return {
            'rsi_14': rsi,
            'macd_value': macd_value,
            'macd_signal': macd_signal,
            'ema_9': ema_9,
            'ema_21': ema_21,
            'ema_50': ema_50,
            'bb_position': bb_position,
            'atr_14': atr,
            'pcr': oi_data.get('pcr', 1.0),
            'vix': vix_data.get('vix', 15.0),
            'hour': now.hour,
            'day_of_week': now.weekday(),
            'us_market_change': us_change
        }
        
    except Exception as e:
        logger.error(f"Error extracting XGBoost features: {e}")
        return {}


def _calculate_xgb_consensus(xgb_direction: int, xgb_confidence: float,
                              groq_pred: dict, gemini_pred: dict) -> dict:
    """
    Calculate weighted consensus with XGBoost (60%) + Groq (20%) + Gemini (20%).
    
    Args:
        xgb_direction: XGBoost direction (1, -1, 0)
        xgb_confidence: XGBoost confidence (0-100)
        groq_pred: Groq prediction dict
        gemini_pred: Gemini prediction dict
    
    Returns:
        Consensus dict with weighted prediction
    """
    # Convert XGBoost direction to text
    xgb_dir_text = _direction_to_text(xgb_direction)
    
    # Get LLM directions
    groq_dir = groq_pred.get("direction", "NEUTRAL")
    gemini_dir = gemini_pred.get("direction", "NEUTRAL")
    groq_conf = groq_pred.get("confidence", 0)
    gemini_conf = gemini_pred.get("confidence", 0)
    
    # Check for LLM errors
    groq_error = "error" in groq_pred
    gemini_error = "error" in gemini_pred
    
    # If both LLMs failed, use XGBoost only
    if groq_error and gemini_error:
        return {
            "consensus": "XGB_ONLY",
            "direction": xgb_dir_text,
            "confidence": int(xgb_confidence),
            "agreement": "XGB_ONLY",
            "xgb_direction": xgb_dir_text,
            "xgb_confidence": xgb_confidence,
            "groq_prediction": groq_pred,
            "gemini_prediction": gemini_pred,
            "one_line_summary": f"XGBoost only: {xgb_dir_text} ({xgb_confidence:.1f}%)"
        }
    
    # Calculate weighted consensus
    # XGBoost: 60%, Groq: 20%, Gemini: 20%
    
    # Convert directions to numeric votes
    votes = {
        1: 0,   # BULLISH
        -1: 0,  # BEARISH
        0: 0    # SIDEWAYS
    }
    
    # XGBoost vote (60% weight)
    votes[xgb_direction] += 0.6
    
    # Groq vote (20% weight)
    if not groq_error:
        groq_numeric = _text_to_direction(groq_dir)
        votes[groq_numeric] += 0.2
    
    # Gemini vote (20% weight)
    if not gemini_error:
        gemini_numeric = _text_to_direction(gemini_dir)
        votes[gemini_numeric] += 0.2
    
    # Find winning direction
    final_direction_numeric = max(votes, key=votes.get)
    final_direction = _direction_to_text(final_direction_numeric)
    
    # Calculate weighted confidence
    # Weight by agreement level
    if xgb_dir_text == groq_dir == gemini_dir:
        # All agree - boost confidence
        final_confidence = int(
            (xgb_confidence * 0.6 + groq_conf * 0.2 + gemini_conf * 0.2) + 10
        )
        agreement = "FULL"
        consensus = "STRONG"
    elif xgb_dir_text == final_direction:
        # XGBoost agrees with final - moderate confidence
        final_confidence = int(
            xgb_confidence * 0.6 + groq_conf * 0.2 + gemini_conf * 0.2
        )
        agreement = "PARTIAL"
        consensus = "MODERATE"
    else:
        # XGBoost disagrees - reduce confidence
        final_confidence = int(
            (xgb_confidence * 0.6 + groq_conf * 0.2 + gemini_conf * 0.2) - 15
        )
        agreement = "CONFLICTING"
        consensus = "WEAK"
    
    # Cap confidence
    final_confidence = min(95, max(30, final_confidence))
    
    # Merge price targets from LLMs
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
    
    all_reasons = [f"XGBoost ML Model: {xgb_dir_text} ({xgb_confidence:.1f}%)"]
    for reason in groq_reasons + gemini_reasons:
        if reason not in all_reasons and len(all_reasons) < 3:
            all_reasons.append(reason)
    
    return {
        "consensus": consensus,
        "direction": final_direction,
        "confidence": final_confidence,
        "agreement": agreement,
        "price_targets": price_targets,
        "top_3_reasons": all_reasons[:3],
        "xgb_direction": xgb_dir_text,
        "xgb_confidence": xgb_confidence,
        "groq_prediction": groq_pred,
        "gemini_prediction": gemini_pred,
        "groq_direction": groq_dir,
        "gemini_direction": gemini_dir,
        "groq_confidence": groq_conf,
        "gemini_confidence": gemini_conf,
        "one_line_summary": f"{consensus} consensus: {final_direction} ({final_confidence}%)"
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
    Get consensus prediction with XGBoost as primary + Groq/Gemini as fallback.
    
    Prediction hierarchy:
    1. XGBoost (60% weight) - if model exists
    2. Groq (20% weight) - real-time analysis
    3. Gemini (20% weight) - real-time analysis
    
    If XGBoost not available, falls back to Dual-AI consensus (50/50 Groq/Gemini)
    """
    
    # Try XGBoost first (if model exists)
    xgb_direction = None
    xgb_confidence = None
    xgb_available = False
    
    try:
        from xgb_model import predict as xgb_predict
        from prediction_logger import extract_indicator_values
        
        # Extract indicator values for XGBoost
        # We need to get df_candles from somewhere - let's pass it through
        # For now, we'll try to predict if we have the values
        
        # Build indicator values dict from indicator_summary
        indicator_values = _extract_xgb_features(
            indicator_summary, oi_data, vix_data, global_cues
        )
        
        if indicator_values:
            xgb_direction, xgb_confidence = xgb_predict(indicator_values)
            
            if xgb_direction is not None:
                xgb_available = True
                logger.info(f"✓ XGBoost prediction: {xgb_direction} ({xgb_confidence}%)")
    
    except ImportError:
        logger.warning("XGBoost module not available")
    except Exception as e:
        logger.warning(f"XGBoost prediction failed: {e}")
    
    # Build prompt for LLMs
    prompt = _build_analysis_prompt(
        price_data, indicator_summary, oi_data,
        vix_data, news_sentiment, greeks, global_cues, patterns
    )
    
    # Call both LLM APIs in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as executor:
        groq_future = executor.submit(_call_groq_api, prompt)
        gemini_future = executor.submit(_call_gemini_api, prompt)
        
        groq_pred = groq_future.result()
        gemini_pred = gemini_future.result()
    
    # If XGBoost available, use weighted consensus
    if xgb_available:
        consensus = _calculate_xgb_consensus(
            xgb_direction, xgb_confidence,
            groq_pred, gemini_pred
        )
        consensus["model_used"] = "XGBoost + Dual-AI (60/20/20)"
        consensus["xgb_prediction"] = {
            "direction": _direction_to_text(xgb_direction),
            "confidence": xgb_confidence
        }
    else:
        # Fallback to Dual-AI consensus
        consensus = _calculate_consensus(groq_pred, gemini_pred)
        consensus["model_used"] = "Dual-AI Consensus (Groq + Gemini)"
    
    # Add metadata
    consensus["generated_at"] = datetime.now(IST).strftime("%H:%M:%S IST")
    
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
