"""
test_backtesting.py
Test script for backtesting engine

Run this to verify backtesting functionality works correctly.
"""

import sys
from backtesting_engine import BacktestingEngine, quick_backtest


def test_engine_initialization():
    """Test engine can be initialized"""
    print("Testing engine initialization...")
    try:
        engine = BacktestingEngine(symbol="^NSEI", initial_capital=100000)
        print("✓ Engine initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Engine initialization failed: {e}")
        return False


def test_data_fetching():
    """Test historical data fetching"""
    print("\nTesting data fetching...")
    try:
        engine = BacktestingEngine()
        df = engine.fetch_historical_data(days=2, interval="5m")
        
        if df.empty:
            print("✗ No data fetched")
            return False
        
        print(f"✓ Fetched {len(df)} candles")
        return True
    except Exception as e:
        print(f"✗ Data fetching failed: {e}")
        return False


def test_prediction_generation():
    """Test prediction generation"""
    print("\nTesting prediction generation...")
    try:
        engine = BacktestingEngine()
        df = engine.fetch_historical_data(days=2, interval="5m")
        
        if df.empty:
            print("✗ No data for prediction test")
            return False
        
        prediction = engine.generate_prediction(df, 10)
        
        if not prediction or 'direction' not in prediction:
            print("✗ Invalid prediction format")
            return False
        
        print(f"✓ Generated prediction: {prediction['direction']} ({prediction['confidence']}%)")
        return True
    except Exception as e:
        print(f"✗ Prediction generation failed: {e}")
        return False


def test_quick_backtest():
    """Test quick backtest function"""
    print("\nTesting quick backtest (this may take 1-2 minutes)...")
    try:
        results = quick_backtest(days=2, interval="15m", timeframe=30)
        
        if not results or 'summary' not in results:
            print("✗ Invalid backtest results")
            return False
        
        summary = results['summary']
        print(f"✓ Backtest completed:")
        print(f"  - Predictions: {summary['total_predictions']}")
        print(f"  - Win Rate: {summary['win_rate']:.1f}%")
        print(f"  - Return: {summary['return_pct']:.2f}%")
        return True
    except Exception as e:
        print(f"✗ Quick backtest failed: {e}")
        return False


def test_metrics_calculation():
    """Test metrics calculation"""
    print("\nTesting metrics calculation...")
    try:
        engine = BacktestingEngine()
        
        # Add some dummy trades
        engine.trades = [
            {'pnl': 100, 'predicted_direction': 'UP', 'correct': True, 'confidence': 70},
            {'pnl': -50, 'predicted_direction': 'DOWN', 'correct': False, 'confidence': 60},
            {'pnl': 150, 'predicted_direction': 'UP', 'correct': True, 'confidence': 80},
        ]
        
        metrics = engine.calculate_metrics()
        
        if not metrics or 'win_rate' not in metrics:
            print("✗ Invalid metrics format")
            return False
        
        print(f"✓ Metrics calculated:")
        print(f"  - Win Rate: {metrics['win_rate']:.1f}%")
        print(f"  - Total Trades: {metrics['total_trades']}")
        return True
    except Exception as e:
        print(f"✗ Metrics calculation failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("BACKTESTING ENGINE - TEST SUITE")
    print("="*70 + "\n")
    
    tests = [
        ("Engine Initialization", test_engine_initialization),
        ("Data Fetching", test_data_fetching),
        ("Prediction Generation", test_prediction_generation),
        ("Metrics Calculation", test_metrics_calculation),
        ("Quick Backtest", test_quick_backtest),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Backtesting engine is working correctly.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
