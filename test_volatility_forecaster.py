"""
test_volatility_forecaster.py
Quick test script for volatility forecasting
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from volatility_forecaster import get_volatility_forecast, VolatilityForecaster

def create_sample_data(days=30, interval_minutes=5):
    """Create sample OHLCV data for testing"""
    
    # Generate timestamps
    start_date = datetime.now() - timedelta(days=days)
    periods = days * 375 // interval_minutes  # 375 minutes per trading day
    
    dates = pd.date_range(start=start_date, periods=periods, freq=f'{interval_minutes}min')
    
    # Generate realistic price data
    np.random.seed(42)
    base_price = 25000
    returns = np.random.normal(0, 0.001, periods)  # 0.1% std dev
    prices = base_price * np.exp(np.cumsum(returns))
    
    # Create OHLCV data
    df = pd.DataFrame({
        'open': prices * (1 + np.random.uniform(-0.001, 0.001, periods)),
        'high': prices * (1 + np.random.uniform(0, 0.002, periods)),
        'low': prices * (1 + np.random.uniform(-0.002, 0, periods)),
        'close': prices,
        'volume': np.random.randint(1000000, 5000000, periods)
    }, index=dates)
    
    # Ensure high >= open, close and low <= open, close
    df['high'] = df[['open', 'high', 'close']].max(axis=1)
    df['low'] = df[['open', 'low', 'close']].min(axis=1)
    
    return df


def test_basic_functionality():
    """Test basic volatility forecasting"""
    print("\n" + "="*70)
    print("TEST 1: Basic Functionality")
    print("="*70)
    
    # Create sample data
    df = create_sample_data(days=7, interval_minutes=5)
    print(f"✓ Created sample data: {len(df)} candles")
    
    # Get forecast
    forecast = get_volatility_forecast(df, vix_current=15.5)
    
    if 'error' in forecast:
        print(f"✗ Error: {forecast['error']}")
        return False
    
    print(f"✓ Forecast generated successfully")
    
    # Check current volatility
    current_vol = forecast.get('current_volatility', {})
    ensemble = current_vol.get('ensemble', 0)
    print(f"✓ Ensemble Volatility: {ensemble:.2f}%")
    
    # Check regime
    regime = forecast.get('regime', {})
    print(f"✓ Regime: {regime.get('regime', 'N/A')}")
    
    # Check trend
    trend = forecast.get('trend', {})
    print(f"✓ Trend: {trend.get('trend', 'N/A')}")
    
    # Check forecasts
    forecasts = forecast.get('forecasts', {})
    print(f"✓ Forecasts available: {', '.join(forecasts.keys())}")
    
    # Check implications
    implications = forecast.get('implications', {})
    print(f"✓ Options Strategy: {implications.get('options_strategy', 'N/A')}")
    print(f"✓ Risk Level: {implications.get('risk_level', 'N/A')}")
    
    return True


def test_different_volatility_levels():
    """Test with different volatility scenarios"""
    print("\n" + "="*70)
    print("TEST 2: Different Volatility Levels")
    print("="*70)
    
    forecaster = VolatilityForecaster()
    
    # Test different volatility levels
    test_cases = [
        (0.3, "VERY LOW"),
        (0.8, "LOW"),
        (1.2, "NORMAL"),
        (2.0, "ELEVATED"),
        (3.5, "HIGH"),
        (5.0, "EXTREME")
    ]
    
    for vol, expected_regime in test_cases:
        regime = forecaster.detect_volatility_regime(vol)
        actual_regime = regime.get('regime', 'UNKNOWN')
        
        if expected_regime in actual_regime:
            print(f"✓ {vol:.1f}% → {actual_regime}")
        else:
            print(f"✗ {vol:.1f}% → Expected {expected_regime}, got {actual_regime}")
            return False
    
    return True


def test_insufficient_data():
    """Test error handling with insufficient data"""
    print("\n" + "="*70)
    print("TEST 3: Error Handling (Insufficient Data)")
    print("="*70)
    
    # Create very small dataset
    df = create_sample_data(days=1, interval_minutes=5)
    df = df.head(10)  # Only 10 candles
    
    print(f"✓ Created small dataset: {len(df)} candles")
    
    forecast = get_volatility_forecast(df)
    
    if 'error' in forecast:
        print(f"✓ Error handled gracefully: {forecast['error']}")
        return True
    else:
        print(f"✗ Should have returned error for insufficient data")
        return False


def test_all_methods():
    """Test all individual volatility calculation methods"""
    print("\n" + "="*70)
    print("TEST 4: Individual Calculation Methods")
    print("="*70)
    
    df = create_sample_data(days=7, interval_minutes=5)
    forecaster = VolatilityForecaster()
    
    # Test each method
    methods = [
        ('Historical Volatility', forecaster.calculate_historical_volatility(df)),
        ('Parkinson', forecaster.calculate_parkinson_volatility(df)),
        ('Garman-Klass', forecaster.calculate_garman_klass_volatility(df)),
        ('ATR-based', forecaster.calculate_atr_volatility(df))
    ]
    
    for name, result in methods:
        if not result.empty and not result.isna().all():
            last_val = result.iloc[-1]
            print(f"✓ {name}: {last_val:.2f}%")
        else:
            print(f"✗ {name}: Failed to calculate")
            return False
    
    # Test GARCH
    log_returns = np.log(df['close'] / df['close'].shift(1))
    garch_forecast = forecaster.simple_garch_forecast(log_returns, horizon=1)
    
    if garch_forecast:
        print(f"✓ GARCH Forecast: {garch_forecast:.2f}%")
    else:
        print(f"✗ GARCH Forecast: Failed")
        return False
    
    return True


def test_hv_vix_analysis():
    """Test HV vs VIX analysis"""
    print("\n" + "="*70)
    print("TEST 5: HV vs VIX Analysis")
    print("="*70)
    
    df = create_sample_data(days=7, interval_minutes=5)
    
    # Test with different VIX levels
    test_cases = [
        (15.5, "HV > VIX"),  # Assuming HV will be around 1-2%
        (25.0, "VIX > HV"),
    ]
    
    for vix, expected in test_cases:
        forecast = get_volatility_forecast(df, vix_current=vix)
        
        if 'error' in forecast:
            print(f"✗ Error with VIX={vix}: {forecast['error']}")
            return False
        
        vix_analysis = forecast.get('vix_analysis')
        if vix_analysis:
            interpretation = vix_analysis.get('interpretation', '')
            print(f"✓ VIX={vix}: {interpretation}")
        else:
            print(f"✗ VIX analysis missing for VIX={vix}")
            return False
    
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("VOLATILITY FORECASTER - TEST SUITE")
    print("="*70)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Volatility Regimes", test_different_volatility_levels),
        ("Error Handling", test_insufficient_data),
        ("Calculation Methods", test_all_methods),
        ("HV vs VIX Analysis", test_hv_vix_analysis),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} FAILED with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Volatility forecaster is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
    
    print("="*70)


if __name__ == "__main__":
    run_all_tests()
