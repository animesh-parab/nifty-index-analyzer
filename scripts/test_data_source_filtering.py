"""
test_data_source_filtering.py
Test data source filtering in prediction logger

This verifies that:
1. Real-time data (NSE, Angel One) is logged
2. Delayed data (yfinance) is NOT logged
3. Visual indicator shows correct status
"""

import pandas as pd
import os
from prediction_logger import log_prediction

LOG_FILE = 'prediction_log.csv'

def test_data_source_filtering():
    """Test that yfinance data is filtered out"""
    print("\n" + "="*70)
    print("DATA SOURCE FILTERING TEST")
    print("="*70)
    
    # Backup existing log if it exists
    backup_created = False
    if os.path.exists(LOG_FILE):
        backup_file = LOG_FILE + '.backup'
        os.rename(LOG_FILE, backup_file)
        backup_created = True
        print(f"✅ Backed up existing log to {backup_file}")
    
    # Create fresh CSV with correct structure
    df_init = pd.DataFrame(columns=[
        'timestamp', 'rsi_14', 'macd_value', 'macd_signal', 
        'ema_9', 'ema_21', 'ema_50', 'bb_position', 'atr_14', 
        'pcr', 'vix', 'hour', 'day_of_week', 'us_market_change',
        'final_direction', 'confidence', 'entry_price', 'data_source', 'actual_outcome'
    ])
    df_init.to_csv(LOG_FILE, index=False)
    print(f"✅ Created fresh test log file")
    
    # Test 1: Real-time data (NSE) should be logged
    print("\n📝 Test 1: NSE API (Real-time) - Should LOG")
    print("-" * 70)
    
    indicator_values_nse = {
        'rsi_14': 55.5,
        'macd_value': 12.3,
        'macd_signal': 10.5,
        'ema_9': 25000,
        'ema_21': 24950,
        'ema_50': 24900,
        'bb_position': 0.6,
        'atr_14': 45.2,
        'pcr': 1.15,
        'vix': 14.5,
        'us_market_change': 0.5,
        'data_source': 'NSE API (Real-time)'  # Real-time source
    }
    
    prediction = {
        'direction': 'BULLISH',
        'confidence': 68
    }
    
    log_prediction(indicator_values_nse, prediction, 25000.5)
    
    # Check if logged
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        if len(df) > 0:
            print(f"✅ PASS: NSE data was logged")
            print(f"   Data source: {df['data_source'].iloc[-1]}")
        else:
            print(f"❌ FAIL: NSE data was NOT logged")
    else:
        print(f"❌ FAIL: Log file not created")
    
    # Test 2: Real-time data (Angel One) should be logged
    print("\n📝 Test 2: Angel One (Real-time) - Should LOG")
    print("-" * 70)
    
    indicator_values_angel = {
        'rsi_14': 56.2,
        'macd_value': 13.1,
        'macd_signal': 11.2,
        'ema_9': 25010,
        'ema_21': 24960,
        'ema_50': 24910,
        'bb_position': 0.65,
        'atr_14': 46.0,
        'pcr': 1.18,
        'vix': 14.8,
        'us_market_change': 0.6,
        'data_source': 'Angel One (Real-time)'  # Real-time source
    }
    
    prediction = {
        'direction': 'BULLISH',
        'confidence': 72
    }
    
    log_prediction(indicator_values_angel, prediction, 25010.5)
    
    # Check if logged
    df = pd.read_csv(LOG_FILE)
    if len(df) == 2:
        print(f"✅ PASS: Angel One data was logged")
        print(f"   Data source: {df['data_source'].iloc[-1]}")
    else:
        print(f"❌ FAIL: Angel One data was NOT logged")
    
    # Test 3: Delayed data (yfinance) should NOT be logged
    print("\n📝 Test 3: yfinance (Delayed) - Should NOT LOG")
    print("-" * 70)
    
    indicator_values_yf = {
        'rsi_14': 57.0,
        'macd_value': 14.0,
        'macd_signal': 12.0,
        'ema_9': 25020,
        'ema_21': 24970,
        'ema_50': 24920,
        'bb_position': 0.7,
        'atr_14': 47.0,
        'pcr': 1.20,
        'vix': 15.0,
        'us_market_change': 0.7,
        'data_source': 'yfinance (15 min delay)'  # Delayed source
    }
    
    prediction = {
        'direction': 'BULLISH',
        'confidence': 75
    }
    
    log_prediction(indicator_values_yf, prediction, 25020.5)
    
    # Check if NOT logged
    df = pd.read_csv(LOG_FILE)
    if len(df) == 2:  # Should still be 2 (not 3)
        print(f"✅ PASS: yfinance data was NOT logged (filtered out)")
        print(f"   Total predictions: {len(df)}")
    else:
        print(f"❌ FAIL: yfinance data was logged (should be filtered)")
        print(f"   Total predictions: {len(df)}")
    
    # Test 4: Check CSV structure
    print("\n📝 Test 4: CSV Structure")
    print("-" * 70)
    
    df = pd.read_csv(LOG_FILE)
    
    # Check for data_source column
    if 'data_source' in df.columns:
        print(f"✅ PASS: data_source column exists")
    else:
        print(f"❌ FAIL: data_source column missing")
    
    # Check column count
    expected_columns = 19
    if len(df.columns) == expected_columns:
        print(f"✅ PASS: {expected_columns} columns present")
    else:
        print(f"❌ FAIL: Expected {expected_columns} columns, got {len(df.columns)}")
    
    # Check data sources
    print(f"\n📊 Data Source Summary:")
    print(df['data_source'].value_counts())
    
    # Verify no yfinance entries
    yfinance_count = df['data_source'].str.contains('yfinance', case=False, na=False).sum()
    if yfinance_count == 0:
        print(f"\n✅ PASS: No yfinance entries in log")
    else:
        print(f"\n❌ FAIL: Found {yfinance_count} yfinance entries")
    
    # Final summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    total_tests = 4
    passed_tests = 0
    
    # Count passes
    if len(df) >= 2:
        passed_tests += 2  # NSE and Angel One logged
    if yfinance_count == 0:
        passed_tests += 1  # yfinance filtered
    if 'data_source' in df.columns and len(df.columns) == expected_columns:
        passed_tests += 1  # CSV structure correct
    
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print(f"✅ ALL TESTS PASSED!")
        print(f"\nData source filtering is working correctly:")
        print(f"  • Real-time data (NSE, Angel One) is logged")
        print(f"  • Delayed data (yfinance) is filtered out")
        print(f"  • CSV structure includes data_source column")
    else:
        print(f"⚠️ SOME TESTS FAILED")
        print(f"\nCheck prediction_logger.py for issues")
    
    # Restore backup
    if backup_created and os.path.exists(LOG_FILE + '.backup'):
        os.remove(LOG_FILE)
        os.rename(LOG_FILE + '.backup', LOG_FILE)
        print(f"\n✅ Restored original log file")
    elif os.path.exists(LOG_FILE):
        # Clean up test file if no backup
        os.remove(LOG_FILE)
        print(f"\n✅ Cleaned up test log file")
    
    print("="*70)


if __name__ == "__main__":
    test_data_source_filtering()
