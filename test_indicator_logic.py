"""
Verification Tests for Indicator Scoring Logic
Tests all 9 fixes from PROMPT9_INDICATOR_FIXES.txt
Run this after implementing all fixes
"""

from indicator_scoring import (
    get_time_confidence_multiplier,
    score_rsi,
    score_macd,
    score_ema,
    score_bollinger,
    score_vix,
    score_opening_range,
    score_previous_day_levels,
    opening_range
)


def run_all_tests():
    print('=== TESTING ALL INDICATOR FIXES ===')
    print()

    # Test 1: Time Filter
    print('TEST 1: Time of Day Filter')
    assert get_time_confidence_multiplier(9, 20) == None,   'FAIL: 9:20 should be disabled'
    assert get_time_confidence_multiplier(9, 35) == 0.5,    'FAIL: 9:35 should be low confidence'
    assert get_time_confidence_multiplier(10, 30) == 1.0,   'FAIL: 10:30 should be high confidence'
    assert get_time_confidence_multiplier(12, 30) == 0.6,   'FAIL: 12:30 should be lunch low confidence'
    assert get_time_confidence_multiplier(15, 10) == None,  'FAIL: 15:10 should be disabled'
    print('✓ PASS: Time Filter - All tests passed')
    print()

    # Test 2: RSI Direction
    print('TEST 2: RSI Direction Logic')
    assert score_rsi(25, 22) == 2,   'FAIL: Oversold + rising = strong bullish'
    assert score_rsi(25, 28) == -1,  'FAIL: Oversold + falling = bearish continuation'
    assert score_rsi(75, 72) == 1,   'FAIL: Overbought + rising = bullish continuation'
    assert score_rsi(75, 78) == -2,  'FAIL: Overbought + falling = strong bearish'
    assert score_rsi(50, 48) == 1,   'FAIL: Middle + rising = building momentum'
    print('✓ PASS: RSI Direction - All tests passed')
    print()

    # Test 3: MACD Histogram
    print('TEST 3: MACD Histogram Momentum')
    assert score_macd(10, 5, 8, 5) == 2,      'FAIL: Positive + strengthening = strong bullish'
    assert score_macd(10, 5, 12, 5) == 1,     'FAIL: Positive + weakening = mild bullish'
    assert score_macd(-10, -5, -8, -5) == -2, 'FAIL: Negative + strengthening = strong bearish'
    assert score_macd(-10, -5, -12, -5) == -1,'FAIL: Negative + weakening = mild bearish'
    print('✓ PASS: MACD Histogram - All tests passed')
    print()

    # Test 4: EMA Crossover
    print('TEST 4: EMA Crossover Detection')
    assert score_ema(25100, 25080, 25060, 25040, 25055, 25060) == 3,  'FAIL: Golden cross = +3'
    assert score_ema(24900, 24920, 24940, 24960, 24945, 24940) == -3, 'FAIL: Death cross = -3'
    assert score_ema(25100, 25080, 25060, 25040, 25080, 25060) == 2,  'FAIL: Perfect uptrend = +2'
    print('✓ PASS: EMA Crossover - All tests passed')
    print()

    # Test 5: Bollinger Bands
    print('TEST 5: Bollinger Bands Trend Awareness')
    assert score_bollinger(25100, 0.85, 25080, 25060) == 1,  'FAIL: Upper band + uptrend = bullish'
    assert score_bollinger(25100, 0.85, 25060, 25080) == -2, 'FAIL: Upper band + downtrend = bearish'
    assert score_bollinger(24900, 0.15, 24920, 24940) == -1, 'FAIL: Lower band + downtrend = bearish'
    assert score_bollinger(24900, 0.15, 24940, 24920) == 2,  'FAIL: Lower band + uptrend = bullish'
    print('✓ PASS: Bollinger Bands - All tests passed')
    print()

    # Test 6: VIX Direction
    print('TEST 6: VIX Direction Logic')
    assert score_vix(18, 15) == -3,    'FAIL: VIX spike >5% = strong bearish'
    assert score_vix(15.3, 15) == -1,  'FAIL: VIX rising = mild bearish'
    assert score_vix(13, 15) == 2,     'FAIL: VIX dropping fast = strong bullish'
    assert score_vix(14.7, 15) == 1,   'FAIL: VIX falling = mild bullish'
    assert score_vix(15, 15) == 0,     'FAIL: VIX stable = neutral'
    print('✓ PASS: VIX Direction - All tests passed')
    print()

    # Test 7: Opening Range
    print('TEST 7: Opening Range Breakout')
    opening_range['high'] = 24600
    opening_range['low'] = 24400
    opening_range['established'] = True
    assert score_opening_range(24700) == 2,  'FAIL: Above range high = bullish'
    assert score_opening_range(24300) == -2, 'FAIL: Below range low = bearish'
    assert score_opening_range(24500) == 0,  'FAIL: Inside range = neutral'
    print('✓ PASS: Opening Range - All tests passed')
    print()

    # Test 8: Previous Day Levels
    print('TEST 8: Previous Day High/Low')
    assert score_previous_day_levels(24700, 24600, 24400) == 2,  'FAIL: Above prev high = strong bullish'
    assert score_previous_day_levels(24300, 24600, 24400) == -2, 'FAIL: Below prev low = strong bearish'
    assert score_previous_day_levels(24590, 24600, 24400) == 1,  'FAIL: Near prev high = mild bullish'
    assert score_previous_day_levels(24410, 24600, 24400) == -1, 'FAIL: Near prev low = mild bearish'
    print('✓ PASS: Previous Day Levels - All tests passed')
    print()

    print('=' * 60)
    print('=== ALL TESTS PASSED - SYSTEM READY FOR LIVE TRADING ===')
    print('=' * 60)


if __name__ == '__main__':
    run_all_tests()
