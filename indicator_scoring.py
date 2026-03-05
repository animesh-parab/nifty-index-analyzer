"""
Enhanced Indicator Scoring Logic
Implements 9 fixes from PROMPT9_INDICATOR_FIXES.txt
Created: March 4, 2026
"""

import pandas as pd
import pandas_ta as ta


# ================================================================
# FIX 1 — TIME OF DAY FILTER
# ================================================================

def get_time_confidence_multiplier(hour, minute):
    """
    Returns confidence multiplier based on time of day.
    Returns None to skip prediction entirely during disabled zones.
    """
    time = hour * 60 + minute  # convert to minutes

    # Disabled zones - skip prediction entirely
    if time < 555:   # Before 9:15
        return None
    if time < 570:   # 9:15-9:30 opening volatility
        return None
    if time > 900:   # After 3:00 closing volatility
        return None

    # Low confidence zones
    if time < 585:          # 9:30-9:45
        return 0.5
    if 720 < time < 780:    # 12:00-1:00 lunch hour
        return 0.6
    if time > 870:          # 2:30-3:00
        return 0.7

    # High confidence zones (10:00-12:00 and 1:30-2:30)
    return 1.0


# ================================================================
# FIX 2 — RSI DIRECTION LOGIC
# ================================================================

def score_rsi(current_rsi, previous_rsi):
    """
    RSI scoring with direction awareness.
    Considers both level and momentum.
    """
    rsi_direction = current_rsi - previous_rsi

    if current_rsi < 30:
        if rsi_direction > 0:   # oversold AND rising
            return 2            # Strong bullish reversal
        else:                   # oversold AND falling
            return -1           # Bearish continuation

    elif current_rsi > 70:
        if rsi_direction > 0:   # overbought AND rising
            return 1            # Bullish continuation
        else:                   # overbought AND falling
            return -2           # Strong bearish reversal

    elif 40 < current_rsi < 60:
        if rsi_direction > 0:
            return 1            # Building momentum
        else:
            return -1           # Losing momentum

    return 0  # neutral


# ================================================================
# FIX 3 — MACD HISTOGRAM MOMENTUM
# ================================================================

def score_macd(macd_value, macd_signal, prev_macd_value, prev_macd_signal):
    """
    MACD scoring using histogram momentum.
    Detects strengthening vs weakening trends.
    """
    histogram = macd_value - macd_signal
    prev_histogram = prev_macd_value - prev_macd_signal
    histogram_change = histogram - prev_histogram

    if histogram > 0 and histogram_change > 0:
        return 2    # Bullish and strengthening
    elif histogram > 0 and histogram_change < 0:
        return 1    # Bullish but weakening
    elif histogram < 0 and histogram_change < 0:
        return -2   # Bearish and strengthening
    elif histogram < 0 and histogram_change > 0:
        return -1   # Bearish but weakening
    return 0


# ================================================================
# FIX 4 — EMA CROSSOVER DETECTION
# ================================================================

def score_ema(price, ema9, ema21, ema50, prev_ema9, prev_ema21):
    """
    EMA scoring with golden cross / death cross detection.
    Combines trend structure with crossover signals.
    """
    score = 0

    # Trend structure
    if price > ema9 > ema21 > ema50:
        score += 2   # Perfect uptrend
    elif price < ema9 < ema21 < ema50:
        score -= 2   # Perfect downtrend

    # EMA9/21 crossover (strongest signal)
    if prev_ema9 < prev_ema21 and ema9 > ema21:
        score += 3   # Golden cross
    elif prev_ema9 > prev_ema21 and ema9 < ema21:
        score -= 3   # Death cross

    return max(min(score, 3), -3)  # cap between -3 and +3


# ================================================================
# FIX 5 — BOLLINGER BANDS WITH TREND AWARENESS
# ================================================================

def score_bollinger(price, bb_position, ema9, ema21):
    """
    Bollinger Bands scoring with trend context.
    Near upper band in uptrend = bullish (riding band).
    Near upper band in downtrend = bearish (resistance).
    """
    trending_up = ema9 > ema21
    trending_down = ema9 < ema21

    if bb_position > 0.8:       # Near upper band
        if trending_up:
            return 1            # Riding upper band = bullish continuation
        else:
            return -2           # Near upper band in downtrend = bearish

    elif bb_position < 0.2:     # Near lower band
        if trending_down:
            return -1           # Riding lower band = bearish continuation
        else:
            return 2            # Near lower band in uptrend = bullish

    return 0  # middle = neutral


# ================================================================
# FIX 6 — VIX DIRECTION INSTEAD OF LEVEL
# ================================================================

def score_vix(current_vix, previous_vix):
    """
    VIX scoring based on direction and rate of change.
    VIX direction matters more than VIX level.
    """
    vix_change = current_vix - previous_vix
    vix_change_pct = vix_change / previous_vix * 100

    if vix_change_pct > 5:      # VIX spiking fast
        return -3               # Strong bearish fear signal
    elif vix_change_pct > 2:    # VIX rising
        return -1               # Mild bearish
    elif vix_change_pct < -5:   # VIX dropping fast
        return 2                # Strong bullish confidence
    elif vix_change_pct < -2:   # VIX falling
        return 1                # Mild bullish
    return 0  # stable


# ================================================================
# FIX 7 — ADX TREND REGIME DETECTION
# ================================================================

def get_market_regime(high, low, close):
    """
    Detect if market is trending or ranging using ADX.
    Returns: 'TRENDING', 'RANGING', or 'NEUTRAL'
    """
    adx = ta.adx(high, low, close, length=14)
    adx_value = adx['ADX_14'].iloc[-1]

    if adx_value > 25:
        return 'TRENDING'
    elif adx_value < 20:
        return 'RANGING'
    else:
        return 'NEUTRAL'


def get_indicator_weights(regime):
    """
    Adjust indicator weights based on market regime.
    Trending markets: favor MACD/EMA
    Ranging markets: favor RSI/BB
    """
    if regime == 'TRENDING':
        return {
            'rsi': 0.10,
            'macd': 0.30,
            'ema': 0.30,
            'bb': 0.05,
            'vix': 0.15,
            'global': 0.10
        }
    elif regime == 'RANGING':
        return {
            'rsi': 0.30,
            'macd': 0.10,
            'ema': 0.10,
            'bb': 0.30,
            'vix': 0.10,
            'global': 0.10
        }
    else:  # NEUTRAL
        return {
            'rsi': 0.20,
            'macd': 0.20,
            'ema': 0.20,
            'bb': 0.10,
            'vix': 0.15,
            'global': 0.15
        }


# ================================================================
# FIX 8 — OPENING RANGE BREAKOUT SIGNAL
# ================================================================

# Global state for opening range (reset daily)
opening_range = {
    'high': None,
    'low': None,
    'established': False
}


def update_opening_range(price, hour, minute):
    """
    Track high and low of first 15 mins after 9:30.
    Call this on every price update during 9:30-9:45.
    """
    time = hour * 60 + minute
    if 570 <= time <= 585:  # 9:30-9:45
        if opening_range['high'] is None or price > opening_range['high']:
            opening_range['high'] = price
        if opening_range['low'] is None or price < opening_range['low']:
            opening_range['low'] = price
        opening_range['established'] = True


def score_opening_range(price):
    """
    Score based on opening range breakout.
    Price breaking above/below this range is a strong signal.
    """
    if not opening_range['established']:
        return 0
    if price > opening_range['high']:
        return 2    # Breakout above range = bullish
    elif price < opening_range['low']:
        return -2   # Breakdown below range = bearish
    return 0        # Inside range = neutral


def reset_opening_range():
    """
    Reset opening range at start of new day.
    Call this at 9:15 AM daily.
    """
    opening_range['high'] = None
    opening_range['low'] = None
    opening_range['established'] = False


# ================================================================
# FIX 9 — PREVIOUS DAY HIGH/LOW LEVELS
# ================================================================

def score_previous_day_levels(price, prev_day_high, prev_day_low):
    """
    Score based on previous day high/low levels.
    These are key support/resistance levels Indian traders watch.
    """
    score = 0
    range_size = prev_day_high - prev_day_low

    if price > prev_day_high:
        score += 2      # Above previous day high = strong bullish
    elif price < prev_day_low:
        score -= 2      # Below previous day low = strong bearish
    elif price > prev_day_high - (range_size * 0.1):
        score += 1      # Near previous day high = mild bullish
    elif price < prev_day_low + (range_size * 0.1):
        score -= 1      # Near previous day low = mild bearish

    return score
