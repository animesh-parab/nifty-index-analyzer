"""
Enhanced Prediction Engine
Integrates new indicator scoring logic with state management
Created: March 4, 2026
"""

from datetime import datetime
import pandas as pd
import pytz

from indicator_scoring import (
    get_time_confidence_multiplier,
    score_rsi,
    score_macd,
    score_ema,
    score_bollinger,
    score_vix,
    score_news,
    get_market_regime,
    get_indicator_weights,
    score_opening_range,
    score_previous_day_levels
)
from prediction_state import prediction_state

IST = pytz.timezone('Asia/Kolkata')


def get_enhanced_prediction(
    price_data: dict,
    indicator_summary: dict,
    df_candles: pd.DataFrame,
    oi_data: dict,
    vix_data: dict,
    news_data: dict
) -> dict:
    """
    Enhanced prediction using new indicator scoring logic.
    Returns None if time filter blocks prediction.
    """
    
    # Get current time
    now = datetime.now(IST)
    hour = now.hour
    minute = now.minute
    
    # ═══════════════════════════════════════════════════════════════
    # FIX 1: TIME OF DAY FILTER (RUNS FIRST)
    # ═══════════════════════════════════════════════════════════════
    time_multiplier = get_time_confidence_multiplier(hour, minute)
    
    if time_multiplier is None:
        # Skip prediction entirely during disabled zones
        return None
    
    # Extract current indicator values
    current_price = price_data.get('price', 0)
    current_rsi = indicator_summary.get('RSI', {}).get('value', 50)
    current_vix = vix_data.get('vix', 15)
    
    # Get MACD values from last candle
    last_candle = df_candles.iloc[-1] if not df_candles.empty else {}
    current_macd_value = indicator_summary.get('MACD', {}).get('value', 0)
    current_macd_signal = last_candle.get('macd_signal', 0)
    
    # Get EMA values
    current_ema9 = indicator_summary.get('EMA_Trend', {}).get('ema_9', 0)
    current_ema21 = indicator_summary.get('EMA_Trend', {}).get('ema_21', 0)
    current_ema50 = indicator_summary.get('EMA_Trend', {}).get('ema_50', 0)
    
    # Get Bollinger Band position
    bb_upper = last_candle.get('bb_upper', 0)
    bb_lower = last_candle.get('bb_lower', 0)
    bb_range = bb_upper - bb_lower
    bb_position = (current_price - bb_lower) / bb_range if bb_range > 0 else 0.5
    
    # ═══════════════════════════════════════════════════════════════
    # FIX 7: ADX REGIME DETECTION (RUNS BEFORE SCORING)
    # ═══════════════════════════════════════════════════════════════
    regime = 'NEUTRAL'
    weights = get_indicator_weights('NEUTRAL')
    
    if not df_candles.empty and len(df_candles) >= 14:
        try:
            regime = get_market_regime(
                df_candles['high'],
                df_candles['low'],
                df_candles['close']
            )
            weights = get_indicator_weights(regime)
            prediction_state.current_regime = regime
        except Exception as e:
            # Fallback to neutral if ADX calculation fails
            regime = 'NEUTRAL'
            weights = get_indicator_weights('NEUTRAL')
    
    # ═══════════════════════════════════════════════════════════════
    # UPDATE OPENING RANGE (FIX 8)
    # ═══════════════════════════════════════════════════════════════
    prediction_state.update_opening_range(current_price, now)
    
    # ═══════════════════════════════════════════════════════════════
    # CALCULATE INDICATOR SCORES
    # ═══════════════════════════════════════════════════════════════
    scores = {}
    reasons = []
    
    # Check if we have previous values for direction-based scoring
    if not prediction_state.has_previous_values():
        # First prediction - initialize state and use neutral scores
        prediction_state.update_indicators(
            current_rsi, current_macd_value, current_macd_signal,
            current_ema9, current_ema21, current_vix
        )
        
        # Use simplified scoring for first prediction
        scores['rsi'] = 0
        scores['macd'] = 0
        scores['ema'] = 0
        scores['bb'] = 0
        scores['vix'] = 0
        reasons.append("First prediction - initializing state")
    else:
        # FIX 2: RSI Direction
        scores['rsi'] = score_rsi(current_rsi, prediction_state.prev_rsi)
        if scores['rsi'] != 0:
            reasons.append(f"RSI: {scores['rsi']:+d} (current={current_rsi:.1f}, prev={prediction_state.prev_rsi:.1f})")
        
        # FIX 3: MACD Histogram Momentum
        scores['macd'] = score_macd(
            current_macd_value, current_macd_signal,
            prediction_state.prev_macd_value, prediction_state.prev_macd_signal
        )
        if scores['macd'] != 0:
            histogram = current_macd_value - current_macd_signal
            reasons.append(f"MACD: {scores['macd']:+d} (histogram={histogram:.1f})")
        
        # FIX 4: EMA Crossover
        scores['ema'] = score_ema(
            current_price, current_ema9, current_ema21, current_ema50,
            prediction_state.prev_ema9, prediction_state.prev_ema21
        )
        if scores['ema'] != 0:
            reasons.append(f"EMA: {scores['ema']:+d}")
        
        # FIX 5: Bollinger Bands with Trend
        scores['bb'] = score_bollinger(
            current_price, bb_position, current_ema9, current_ema21
        )
        if scores['bb'] != 0:
            reasons.append(f"BB: {scores['bb']:+d} (position={bb_position:.2f})")
        
        # FIX 6: VIX Direction
        scores['vix'] = score_vix(current_vix, prediction_state.prev_vix)
        if scores['vix'] != 0:
            vix_change_pct = (current_vix - prediction_state.prev_vix) / prediction_state.prev_vix * 100
            reasons.append(f"VIX: {scores['vix']:+d} (change={vix_change_pct:+.1f}%)")
    
    # FIX 8: Opening Range Breakout
    scores['opening_range'] = score_opening_range(current_price)
    if scores['opening_range'] != 0:
        or_data = prediction_state.get_opening_range()
        reasons.append(f"Opening Range: {scores['opening_range']:+d} (H={or_data['high']}, L={or_data['low']})")
    
    # FIX 9: Previous Day Levels
    prev_day = prediction_state.get_previous_day_levels()
    if prev_day['high'] and prev_day['low']:
        scores['prev_day'] = score_previous_day_levels(
            current_price, prev_day['high'], prev_day['low']
        )
        if scores['prev_day'] != 0:
            reasons.append(f"Prev Day: {scores['prev_day']:+d} (H={prev_day['high']:.0f}, L={prev_day['low']:.0f})")
    else:
        scores['prev_day'] = 0
    
    # FIX 10: News Sentiment
    scores['news'] = score_news(news_data)
    if scores['news'] != 0:
        sentiment_text = news_data.get('overall', 'N/A')
        sentiment_score = news_data.get('score', 0)
        reasons.append(f"News: {scores['news']:+d} ({sentiment_text}, {sentiment_score:+.2f})")
    
    # Global market sentiment (simple scoring)
    scores['global'] = 0
    # Add simple global scoring if needed
    
    # ═══════════════════════════════════════════════════════════════
    # CALCULATE WEIGHTED SCORE USING REGIME-BASED WEIGHTS
    # ═══════════════════════════════════════════════════════════════
    weighted_score = (
        scores.get('rsi', 0) * weights['rsi'] +
        scores.get('macd', 0) * weights['macd'] +
        scores.get('ema', 0) * weights['ema'] +
        scores.get('bb', 0) * weights['bb'] +
        scores.get('vix', 0) * weights['vix'] +
        scores.get('news', 0) * weights['news'] +
        scores.get('opening_range', 0) * 0.15 +  # Fixed weight
        scores.get('prev_day', 0) * 0.10 +  # Fixed weight
        scores.get('global', 0) * weights['global']
    )
    
    # Apply time-of-day multiplier
    final_score = weighted_score * time_multiplier
    
    # ═══════════════════════════════════════════════════════════════
    # DETERMINE DIRECTION AND CONFIDENCE
    # ═══════════════════════════════════════════════════════════════
    if final_score >= 1.5:
        direction = "BULLISH"
        confidence = min(85, 50 + int(final_score * 10))
        strength = "STRONG"
    elif final_score >= 0.5:
        direction = "BULLISH"
        confidence = min(70, 45 + int(final_score * 10))
        strength = "MODERATE"
    elif final_score <= -1.5:
        direction = "BEARISH"
        confidence = min(85, 50 + int(abs(final_score) * 10))
        strength = "STRONG"
    elif final_score <= -0.5:
        direction = "BEARISH"
        confidence = min(70, 45 + int(abs(final_score) * 10))
        strength = "MODERATE"
    else:
        direction = "SIDEWAYS"
        confidence = 40
        strength = "WEAK"
    
    # Update state for next prediction
    prediction_state.update_indicators(
        current_rsi, current_macd_value, current_macd_signal,
        current_ema9, current_ema21, current_vix
    )
    
    # ═══════════════════════════════════════════════════════════════
    # BUILD RESPONSE
    # ═══════════════════════════════════════════════════════════════
    return {
        "direction": direction,
        "confidence": confidence,
        "strength": strength,
        "consensus": "ENHANCED_SCORING",
        "agreement": regime,  # Show market regime in agreement field
        "top_3_reasons": reasons[:3],
        "one_line_summary": f"Enhanced: {direction} ({confidence}%) | {regime} market | Time multiplier: {time_multiplier}x",
        "model_used": "Enhanced Indicator Scoring v2.0",
        "generated_at": now.strftime("%H:%M:%S IST"),
        "raw_score": round(weighted_score, 2),
        "final_score": round(final_score, 2),
        "time_multiplier": time_multiplier,
        "market_regime": regime,
        "indicator_weights": weights,
        "all_scores": scores
    }


def initialize_previous_day_levels(df_candles: pd.DataFrame):
    """
    Initialize previous day high/low from historical data.
    Call this at system startup.
    """
    if df_candles.empty or len(df_candles) < 2:
        return
    
    try:
        # Get yesterday's data (assuming last full day in dataframe)
        yesterday_data = df_candles[:-1]  # Exclude today
        if not yesterday_data.empty:
            prev_high = yesterday_data['high'].max()
            prev_low = yesterday_data['low'].min()
            prev_date = yesterday_data.index[-1].date() if hasattr(yesterday_data.index[-1], 'date') else None
            
            prediction_state.update_previous_day_levels(prev_high, prev_low, prev_date)
    except Exception as e:
        # Silently fail - not critical
        pass
