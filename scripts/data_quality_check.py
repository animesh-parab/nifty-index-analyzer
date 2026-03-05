"""
Comprehensive data quality check for prediction_log.csv
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

LOG_FILE = "prediction_log.csv"

def check_data_quality():
    """Check data quality and identify any issues"""
    
    df = pd.read_csv(LOG_FILE)
    
    print("="*70)
    print("DATA QUALITY REPORT")
    print("="*70)
    
    # Basic stats
    print(f"\n1. BASIC STATS:")
    print(f"   Total rows: {len(df)}")
    print(f"   With outcomes: {df['actual_outcome'].notna().sum()}")
    print(f"   Without outcomes: {df['actual_outcome'].isna().sum()}")
    
    # Check for duplicates
    print(f"\n2. DUPLICATE CHECK:")
    duplicates = df.duplicated(subset=['timestamp'], keep=False)
    print(f"   Duplicate timestamps: {duplicates.sum()}")
    if duplicates.sum() > 0:
        print("   ⚠️  WARNING: Found duplicate timestamps!")
        print(df[duplicates][['timestamp', 'entry_price', 'final_direction']])
    else:
        print("   ✅ No duplicates")
    
    # Check for missing/zero values in critical columns
    print(f"\n3. MISSING/ZERO VALUES:")
    critical_cols = ['rsi_14', 'macd_value', 'ema_9', 'ema_21', 'ema_50', 'vix', 'entry_price']
    issues = []
    for col in critical_cols:
        zero_count = (df[col] == 0).sum()
        null_count = df[col].isna().sum()
        if zero_count > 0 or null_count > 0:
            issues.append(f"   ⚠️  {col}: {zero_count} zeros, {null_count} nulls")
    
    if issues:
        for issue in issues:
            print(issue)
    else:
        print("   ✅ All critical columns have valid values")
    
    # Check for unrealistic values
    print(f"\n4. UNREALISTIC VALUES:")
    unrealistic = []
    
    # RSI should be 0-100
    bad_rsi = df[(df['rsi_14'] < 0) | (df['rsi_14'] > 100)]
    if len(bad_rsi) > 0:
        unrealistic.append(f"   ⚠️  RSI out of range (0-100): {len(bad_rsi)} rows")
    
    # VIX typically 10-40
    bad_vix = df[(df['vix'] < 5) | (df['vix'] > 50)]
    if len(bad_vix) > 0:
        unrealistic.append(f"   ⚠️  VIX unusual (<5 or >50): {len(bad_vix)} rows")
    
    # Entry price should be reasonable (20000-30000 for Nifty)
    bad_price = df[(df['entry_price'] < 20000) | (df['entry_price'] > 30000)]
    if len(bad_price) > 0:
        unrealistic.append(f"   ⚠️  Entry price unusual: {len(bad_price)} rows")
    
    if unrealistic:
        for issue in unrealistic:
            print(issue)
    else:
        print("   ✅ All values within realistic ranges")
    
    # Check time intervals
    print(f"\n5. TIME INTERVAL CHECK:")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    df['time_diff'] = df['timestamp'].diff().dt.total_seconds()
    
    # Intervals should be ~60 seconds (allow 50-70)
    good_intervals = df[(df['time_diff'] >= 50) & (df['time_diff'] <= 70)]
    bad_intervals = df[(df['time_diff'] < 50) | (df['time_diff'] > 70)]
    bad_intervals = bad_intervals[bad_intervals['time_diff'].notna()]
    
    print(f"   Good intervals (50-70s): {len(good_intervals)}")
    print(f"   Bad intervals: {len(bad_intervals)}")
    
    if len(bad_intervals) > 0:
        print(f"   ⚠️  WARNING: {len(bad_intervals)} irregular intervals")
        print("\n   Sample of bad intervals:")
        print(bad_intervals[['timestamp', 'time_diff']].head(10).to_string(index=False))
    else:
        print("   ✅ All intervals consistent")
    
    # Check data source distribution
    print(f"\n6. DATA SOURCE:")
    source_counts = df['data_source'].value_counts()
    for source, count in source_counts.items():
        pct = (count / len(df)) * 100
        print(f"   {source}: {count} ({pct:.1f}%)")
    
    # Check outcome distribution
    print(f"\n7. OUTCOME DISTRIBUTION:")
    outcome_counts = df['actual_outcome'].value_counts()
    total_with_outcomes = df['actual_outcome'].notna().sum()
    for outcome, count in outcome_counts.items():
        pct = (count / total_with_outcomes) * 100
        outcome_label = {1.0: 'UP', 0.0: 'SIDEWAYS', -1.0: 'DOWN'}.get(outcome, outcome)
        print(f"   {outcome_label}: {count} ({pct:.1f}%)")
    
    # Check for market hours violations
    print(f"\n8. MARKET HOURS CHECK:")
    df['hour'] = df['timestamp'].dt.hour
    df['minute'] = df['timestamp'].dt.minute
    
    # Market hours: 9:15 AM - 3:30 PM (9-15 hours)
    outside_hours = df[
        (df['hour'] < 9) | 
        (df['hour'] > 15) | 
        ((df['hour'] == 9) & (df['minute'] < 15)) |
        ((df['hour'] == 15) & (df['minute'] > 30))
    ]
    
    if len(outside_hours) > 0:
        print(f"   ⚠️  WARNING: {len(outside_hours)} rows outside market hours")
        print("\n   Outside market hours:")
        print(outside_hours[['timestamp', 'entry_price']].to_string(index=False))
    else:
        print("   ✅ All data within market hours")
    
    # Final verdict
    print("\n" + "="*70)
    print("FINAL VERDICT:")
    print("="*70)
    
    total_issues = (
        duplicates.sum() + 
        len(issues) + 
        len(unrealistic) + 
        len(bad_intervals) + 
        len(outside_hours)
    )
    
    if total_issues == 0:
        print("✅ DATA IS CLEAN - Ready for training!")
    else:
        print(f"⚠️  FOUND {total_issues} ISSUES - Needs cleaning")
        print("\nRecommended actions:")
        if duplicates.sum() > 0:
            print("  - Run: python scripts/remove_duplicates.py")
        if len(issues) > 0:
            print("  - Run: python scripts/remove_invalid_rows.py")
        if len(outside_hours) > 0:
            print("  - Remove rows outside market hours")
    
    print("="*70)

if __name__ == "__main__":
    check_data_quality()
