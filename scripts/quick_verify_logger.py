"""
quick_verify_logger.py
Quick verification script for prediction logger

Run this after dashboard has been running for 20+ minutes
"""

import pandas as pd
import os
from datetime import datetime, timedelta

LOG_FILE = 'prediction_log.csv'

def quick_verify():
    """Quick verification of logger functionality"""
    print("\n" + "="*70)
    print("PREDICTION LOGGER - QUICK VERIFICATION")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Checking: {LOG_FILE}")
    print("="*70)
    
    # Check 1: File exists
    if not os.path.exists(LOG_FILE):
        print("\n❌ FAIL: prediction_log.csv not found")
        print("\nTroubleshooting:")
        print("1. Run dashboard first: streamlit run app.py")
        print("2. Wait for at least one prediction to be made")
        print("3. Check if dashboard is running during market hours (9:15-15:30 IST)")
        return False
    
    print("\n✅ PASS: File exists")
    
    # Check 2: File has data
    try:
        df = pd.read_csv(LOG_FILE)
    except Exception as e:
        print(f"\n❌ FAIL: Could not read CSV file")
        print(f"Error: {e}")
        return False
    
    total = len(df)
    
    if total == 0:
        print("\n❌ FAIL: No predictions logged yet")
        print("\nTroubleshooting:")
        print("1. Dashboard must be running during market hours")
        print("2. Wait for at least one prediction cycle (60 seconds)")
        print("3. Check terminal logs for errors")
        return False
    
    print(f"✅ PASS: {total} predictions logged")
    
    # Check 3: Has correct columns
    expected_columns = [
        'timestamp', 'rsi_14', 'macd_value', 'macd_signal',
        'ema_9', 'ema_21', 'ema_50', 'bb_position', 'atr_14',
        'pcr', 'vix', 'hour', 'day_of_week', 'us_market_change',
        'final_direction', 'confidence', 'entry_price', 'data_source', 'actual_outcome'
    ]
    
    missing_columns = set(expected_columns) - set(df.columns)
    
    if missing_columns:
        print(f"\n❌ FAIL: Missing columns: {missing_columns}")
        return False
    
    print(f"✅ PASS: All {len(expected_columns)} columns present")
    
    # Check 3b: Data source distribution
    if 'data_source' in df.columns:
        print(f"\n📡 Data Source Distribution:")
        source_counts = df['data_source'].value_counts()
        for source, count in source_counts.items():
            pct = (count / total * 100)
            print(f"   {source}: {count} ({pct:.1f}%)")
        
        # Check for delayed data (yfinance)
        yfinance_count = df['data_source'].str.contains('yfinance', case=False, na=False).sum()
        if yfinance_count > 0:
            print(f"\n⚠️ WARNING: {yfinance_count} predictions logged with delayed data (yfinance)")
            print(f"   This should not happen - check prediction_logger.py filter")
        else:
            print(f"\n✅ No delayed data logged (good!)")
    
    # Check 4: Outcome tracking
    with_outcome = df['actual_outcome'].notna().sum()
    pending = total - with_outcome
    
    print(f"\n📊 Outcome Status:")
    print(f"   Total predictions: {total}")
    print(f"   With outcomes: {with_outcome}")
    print(f"   Pending outcomes: {pending}")
    
    if total > 0:
        fill_rate = (with_outcome / total * 100)
        print(f"   Fill rate: {fill_rate:.1f}%")
    
    # Analyze timing
    if with_outcome == 0 and total > 0:
        first_time = datetime.fromisoformat(df['timestamp'].iloc[0])
        now = datetime.now()
        elapsed = (now - first_time).total_seconds() / 60
        
        if elapsed < 15:
            print(f"\n⏳ WAITING: First prediction is {elapsed:.0f} minutes old")
            print(f"   Outcomes will be filled after 15 minutes")
            print(f"   Check again in {15 - elapsed:.0f} minutes")
            return True
        else:
            print(f"\n❌ FAIL: No outcomes filled after {elapsed:.0f} minutes")
            print("\nTroubleshooting:")
            print("1. Check terminal logs for 'Updated outcome' messages")
            print("2. Verify yfinance is working: python -c 'import yfinance; print(yfinance.Ticker(\"^NSEI\").history(period=\"1d\"))'")
            print("3. Check if background threads are running")
            return False
    
    elif with_outcome > 0:
        print(f"\n✅ PASS: Outcome tracking working!")
        
        # Show outcome distribution
        outcomes = df['actual_outcome'].dropna()
        up_count = (outcomes == 1).sum()
        down_count = (outcomes == -1).sum()
        sideways_count = (outcomes == 0).sum()
        
        print(f"\n📈 Outcome Distribution:")
        print(f"   UP (+1): {up_count} ({up_count/len(outcomes)*100:.1f}%)")
        print(f"   DOWN (-1): {down_count} ({down_count/len(outcomes)*100:.1f}%)")
        print(f"   SIDEWAYS (0): {sideways_count} ({sideways_count/len(outcomes)*100:.1f}%)")
        
        # Check if distribution is reasonable
        if up_count == 0 and down_count == 0:
            print(f"\n⚠️ WARNING: All outcomes are SIDEWAYS")
            print(f"   This might indicate low market volatility")
        elif up_count == 0 or down_count == 0:
            print(f"\n⚠️ WARNING: Only one direction observed")
            print(f"   Need more data for balanced training")
        else:
            print(f"\n✅ Balanced outcome distribution")
    
    # Check 5: Recent activity
    if total > 0:
        last_time = datetime.fromisoformat(df['timestamp'].iloc[-1])
        now = datetime.now()
        minutes_since = (now - last_time).total_seconds() / 60
        
        print(f"\n⏰ Recent Activity:")
        print(f"   Last prediction: {last_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Time since: {minutes_since:.0f} minutes ago")
        
        if minutes_since > 120:
            print(f"\n⚠️ WARNING: No recent predictions (>2 hours)")
            print(f"   Dashboard might not be running")
        elif minutes_since > 60:
            print(f"\n⚠️ Note: Last prediction was {minutes_since:.0f} minutes ago")
            print(f"   Normal if outside market hours")
        else:
            print(f"\n✅ Recent activity detected")
    
    # Check 6: Data quality
    print(f"\n🔍 Data Quality Check:")
    
    # Check for missing values in features
    feature_cols = ['rsi_14', 'macd_value', 'ema_9', 'pcr', 'vix']
    missing_features = df[feature_cols].isna().sum()
    
    if missing_features.sum() > 0:
        print(f"   ⚠️ Some features have missing values:")
        for col, count in missing_features[missing_features > 0].items():
            print(f"      {col}: {count} missing")
    else:
        print(f"   ✅ All features populated")
    
    # Check for reasonable values
    if 'confidence' in df.columns:
        avg_conf = df['confidence'].mean()
        print(f"   Average confidence: {avg_conf:.1f}%")
        
        if avg_conf < 40:
            print(f"   ⚠️ Low average confidence")
        elif avg_conf > 90:
            print(f"   ⚠️ Unusually high confidence")
        else:
            print(f"   ✅ Confidence values reasonable")
    
    # Final summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    if with_outcome >= 300:
        print(f"✅ READY TO TRAIN: {with_outcome} predictions with outcomes")
        print(f"   Run: python xgb_model.py")
    elif with_outcome > 0:
        needed = 300 - with_outcome
        print(f"⏳ COLLECTING DATA: {with_outcome}/300 predictions with outcomes")
        print(f"   Need {needed} more samples")
        print(f"   Estimated time: {needed * 2:.0f} minutes (at 1 prediction/2 min)")
    else:
        print(f"⏳ WAITING: {total} predictions logged, waiting for outcomes")
        print(f"   Check again in 15-20 minutes")
    
    print("="*70)
    
    return True


if __name__ == "__main__":
    success = quick_verify()
    
    if success:
        print("\n✅ Verification complete!")
        print("\nNext steps:")
        print("1. Keep dashboard running during market hours")
        print("2. Run this script daily to monitor progress")
        print("3. Once you have 300+ outcomes, train XGBoost model")
    else:
        print("\n❌ Verification failed!")
        print("\nSee troubleshooting steps above")
        print("Or check: LOGGER_VERIFICATION_GUIDE.md")
