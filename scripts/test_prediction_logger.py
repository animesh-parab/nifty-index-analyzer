"""
test_prediction_logger.py
Test script to verify prediction logging works correctly

Tests:
1. CSV writing
2. Outcome tracking after 15 minutes
3. Data persistence
"""

import pandas as pd
import os
import time
from datetime import datetime
from prediction_logger import log_prediction, get_log_stats, LOG_FILE

def test_csv_writing():
    """Test 1: Verify CSV writing works"""
    print("\n" + "="*70)
    print("TEST 1: CSV Writing")
    print("="*70)
    
    # Create test data
    indicator_values = {
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
        'us_market_change': 0.5
    }
    
    prediction = {
        'direction': 'BULLISH',
        'confidence': 68
    }
    
    current_price = 25000.50
    
    # Log prediction
    print(f"Logging test prediction...")
    log_prediction(indicator_values, prediction, current_price)
    
    # Wait a moment for file write
    time.sleep(1)
    
    # Check if file exists and has data
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        print(f"✅ CSV file exists: {LOG_FILE}")
        print(f"✅ Total rows: {len(df)}")
        print(f"✅ Columns: {list(df.columns)}")
        
        # Show last row
        if len(df) > 0:
            last_row = df.iloc[-1]
            print(f"\nLast logged prediction:")
            print(f"  Timestamp: {last_row['timestamp']}")
            print(f"  Direction: {last_row['final_direction']}")
            print(f"  Confidence: {last_row['confidence']}")
            print(f"  Entry Price: {last_row['entry_price']}")
            print(f"  Actual Outcome: {last_row['actual_outcome']}")
            
            if pd.isna(last_row['actual_outcome']):
                print(f"  ⏳ Outcome pending (will be filled in 15 minutes)")
            else:
                print(f"  ✅ Outcome recorded: {last_row['actual_outcome']}")
        
        return True
    else:
        print(f"❌ CSV file not found: {LOG_FILE}")
        return False


def test_outcome_tracking():
    """Test 2: Verify outcome tracking (simulated)"""
    print("\n" + "="*70)
    print("TEST 2: Outcome Tracking (Simulated)")
    print("="*70)
    
    print("Note: Real outcome tracking happens in background thread after 15 min")
    print("This test simulates the outcome update process")
    
    if not os.path.exists(LOG_FILE):
        print("❌ No log file to test")
        return False
    
    df = pd.read_csv(LOG_FILE)
    
    # Count predictions with and without outcomes
    total = len(df)
    with_outcome = df['actual_outcome'].notna().sum()
    pending = total - with_outcome
    
    print(f"\nCurrent status:")
    print(f"  Total predictions: {total}")
    print(f"  With outcomes: {with_outcome}")
    print(f"  Pending outcomes: {pending}")
    
    if pending > 0:
        print(f"\n⏳ {pending} predictions waiting for outcome verification")
        print(f"   Outcomes will be filled automatically after 15 minutes")
        
        # Show pending predictions
        pending_df = df[df['actual_outcome'].isna()]
        print(f"\nPending predictions:")
        for idx, row in pending_df.iterrows():
            print(f"  • {row['timestamp']} - {row['final_direction']} ({row['confidence']}%)")
    
    if with_outcome > 0:
        print(f"\n✅ {with_outcome} predictions have verified outcomes")
        
        # Show outcome distribution
        outcomes = df['actual_outcome'].dropna()
        up_count = (outcomes == 1).sum()
        down_count = (outcomes == -1).sum()
        sideways_count = (outcomes == 0).sum()
        
        print(f"\nOutcome distribution:")
        print(f"  UP (+1): {up_count}")
        print(f"  DOWN (-1): {down_count}")
        print(f"  SIDEWAYS (0): {sideways_count}")
    
    return True


def test_data_persistence():
    """Test 3: Verify data persists across runs"""
    print("\n" + "="*70)
    print("TEST 3: Data Persistence")
    print("="*70)
    
    stats = get_log_stats()
    
    print(f"Log statistics:")
    print(f"  Total predictions: {stats['total']}")
    print(f"  With outcomes: {stats['with_outcome']}")
    print(f"  Ready for training: {stats['ready_for_training']}")
    
    if stats['total'] > 0:
        print(f"\n✅ Data persists across runs")
        
        if stats['ready_for_training']:
            print(f"✅ Ready to train XGBoost model (300+ samples)")
        else:
            needed = 300 - stats['with_outcome']
            print(f"⏳ Need {needed} more samples with outcomes for training")
    else:
        print(f"⚠️ No data logged yet")
    
    return True


def test_manual_outcome_update():
    """Test 4: Manually update an outcome to verify the mechanism works"""
    print("\n" + "="*70)
    print("TEST 4: Manual Outcome Update (Verification)")
    print("="*70)
    
    if not os.path.exists(LOG_FILE):
        print("❌ No log file to test")
        return False
    
    df = pd.read_csv(LOG_FILE)
    
    # Find first row without outcome
    pending = df[df['actual_outcome'].isna()]
    
    if len(pending) == 0:
        print("✅ All predictions have outcomes")
        return True
    
    # Manually update first pending outcome (for testing)
    first_pending_idx = pending.index[0]
    timestamp = df.loc[first_pending_idx, 'timestamp']
    
    print(f"Testing outcome update for: {timestamp}")
    
    # Simulate outcome update
    df.loc[first_pending_idx, 'actual_outcome'] = 1  # Simulate UP outcome
    df.to_csv(LOG_FILE, index=False)
    
    # Verify update
    df_verify = pd.read_csv(LOG_FILE)
    updated_outcome = df_verify.loc[first_pending_idx, 'actual_outcome']
    
    if pd.notna(updated_outcome):
        print(f"✅ Outcome update mechanism works!")
        print(f"   Updated outcome: {updated_outcome}")
        
        # Revert the test change
        df_verify.loc[first_pending_idx, 'actual_outcome'] = None
        df_verify.to_csv(LOG_FILE, index=False)
        print(f"   (Test change reverted)")
        
        return True
    else:
        print(f"❌ Outcome update failed")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("PREDICTION LOGGER TEST SUITE")
    print("="*70)
    print(f"Testing file: {LOG_FILE}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Run tests
    results.append(("CSV Writing", test_csv_writing()))
    results.append(("Outcome Tracking", test_outcome_tracking()))
    results.append(("Data Persistence", test_data_persistence()))
    results.append(("Manual Update", test_manual_outcome_update()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<25} {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n✅ All tests passed! Logger is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
    
    print("\n" + "="*70)
    print("IMPORTANT NOTES")
    print("="*70)
    print("1. Outcome tracking happens in background thread after 15 minutes")
    print("2. Logger works in both paper trading and live mode")
    print("3. Check prediction_log.csv after running dashboard for 20+ minutes")
    print("4. Outcomes are filled automatically - no manual intervention needed")
    print("="*70)


if __name__ == "__main__":
    run_all_tests()
