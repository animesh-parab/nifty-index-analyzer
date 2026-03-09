# eod_merge.py
# Run every day after market close (3:30 PM+)
# Merges V2 data into main CSV

import pandas as pd
import csv
import os
from datetime import datetime
import pytz

IST = pytz.timezone('Asia/Kolkata')
MAIN_CSV = 'prediction_log.csv'
V2_CSV = 'new_logger/predictions_v2.csv'
BACKUP_DIR = 'data/backups/'

def eod_merge():
    print('='*50)
    print('EOD MERGE - Merging V2 into Main CSV')
    print('='*50)
    
    # Step 1: Verify both files exist and load cleanly
    try:
        df_main = pd.read_csv(MAIN_CSV)
        print(f'Main CSV: {len(df_main)} rows ✅')
    except Exception as e:
        print(f'Main CSV ERROR: {e} ❌')
        return
    
    try:
        df_v2 = pd.read_csv(V2_CSV)
        print(f'V2 CSV: {len(df_v2)} rows ✅')
    except Exception as e:
        print(f'V2 CSV ERROR: {e} ❌')
        return
    
    # Step 2: Check columns match
    if list(df_main.columns) != list(df_v2.columns):
        print('Column mismatch ❌')
        print('Main:', list(df_main.columns))
        print('V2:', list(df_v2.columns))
        return
    print('Columns match ✅')
    
    # Step 3: Backup main CSV before merge
    today = datetime.now(IST).strftime('%Y%m%d_%H%M%S')
    backup_path = f'{BACKUP_DIR}prediction_log_before_merge_{today}.csv'
    df_main.to_csv(backup_path, index=False, quoting=2)
    print(f'Backup created: {backup_path} ✅')
    
    # Step 4: Remove duplicates between files
    existing_timestamps = set(df_main['timestamp'].str[:16].values)
    df_v2_new = df_v2[~df_v2['timestamp'].str[:16].isin(existing_timestamps)]
    print(f'New V2 rows (no duplicates): {len(df_v2_new)}')
    
    # Step 5: Merge and save
    df_merged = pd.concat([df_main, df_v2_new], ignore_index=True)
    df_merged = df_merged.sort_values('timestamp').reset_index(drop=True)
    df_merged.to_csv(MAIN_CSV, index=False, quoting=2)
    print(f'Merged CSV saved: {len(df_merged)} rows ✅')
    
    # Step 6: Verify merged file loads cleanly
    try:
        df_verify = pd.read_csv(MAIN_CSV)
        print(f'Verification read: {len(df_verify)} rows ✅')
    except Exception as e:
        print(f'Verification FAILED: {e} ❌')
        print('Restoring from backup...')
        import shutil
        shutil.copy(backup_path, MAIN_CSV)
        print('Restored from backup ✅')
        return
    
    # Step 7: Reset V2 CSV (clear for tomorrow)
    df_empty = pd.DataFrame(columns=df_v2.columns)
    df_empty.to_csv(V2_CSV, index=False, quoting=2)
    print(f'V2 CSV reset for tomorrow ✅')
    
    # Step 8: Summary
    print()
    print('='*50)
    print('MERGE COMPLETE')
    print(f'Before: {len(df_main)} rows')
    print(f'Added:  {len(df_v2_new)} rows')
    print(f'After:  {len(df_merged)} rows')
    print(f'Backup: {backup_path}')
    print('='*50)

if __name__ == '__main__':
    eod_merge()
