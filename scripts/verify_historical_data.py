"""
verify_historical_data.py

Quick verification script for historical training data

Usage: python scripts/verify_historical_data.py
"""

import pandas as pd
import os

print("="*70)
print("HISTORICAL DATA VERIFICATION")
print("="*70)
print()

files_to_check = [
    'historical_training_data.csv',
    'combined_training_data.csv',
    'prediction_log.csv'
]

for filename in files_to_check:
    print(f"Checking {filename}...")
    
    if not os.path.exists(filename):
        print(f"  ❌ File not found")
        print()
        continue
    
    try:
        df = pd.read_csv(filename)
        
        print(f"  ✅ File exists")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {len(df.columns)}")
        
        # Check for outcomes
        if 'actual_outcome' in df.columns:
            outcome_counts = df['actual_outcome'].value_counts().sort_index()
            total_with_outcome = df['actual_outcome'].notna().sum()
            total = len(df)
            
            print(f"  Rows with outcomes: {total_with_outcome}/{total} ({total_with_outcome/total*100:.1f}%)")
            print(f"  Class distribution:")
            
            for outcome, count in outcome_counts.items():
                if pd.notna(outcome):
                    label = {-1: 'DOWN', 0: 'SIDEWAYS', 1: 'UP'}.get(outcome, 'UNKNOWN')
                    percentage = (count / total_with_outcome) * 100
                    print(f"    {label:10s}: {count:5d} ({percentage:5.1f}%)")
        
        # Check date range
        if 'timestamp' in df.columns:
            df['timestamp_dt'] = pd.to_datetime(df['timestamp'])
            print(f"  Date range: {df['timestamp_dt'].min()} to {df['timestamp_dt'].max()}")
        
        # Check for missing values in key columns
        key_columns = ['rsi_14', 'macd_value', 'ema_9', 'ema_21', 'ema_50', 'atr_14', 'vix']
        missing_counts = df[key_columns].isna().sum()
        
        if missing_counts.sum() > 0:
            print(f"  ⚠️  Missing values detected:")
            for col, count in missing_counts.items():
                if count > 0:
                    print(f"    {col}: {count} missing")
        else:
            print(f"  ✅ No missing values in key columns")
        
        print()
        
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        print()

print("="*70)
print("Verification complete!")
print("="*70)
