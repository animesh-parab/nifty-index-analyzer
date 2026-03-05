"""
Remove duplicate predictions from same minute
Keep only the first prediction per minute
"""

import pandas as pd
from datetime import datetime

LOG_FILE = 'prediction_log.csv'
BACKUP_FILE = f'prediction_log_before_dedup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

print("="*70)
print("REMOVING DUPLICATE PREDICTIONS")
print("="*70)

# Backup first
import shutil
shutil.copy(LOG_FILE, BACKUP_FILE)
print(f"\n✅ Backed up to: {BACKUP_FILE}")

# Load data
df = pd.read_csv(LOG_FILE)
print(f"\nOriginal data: {len(df)} predictions")

# Convert timestamp to datetime
df['timestamp_dt'] = pd.to_datetime(df['timestamp'])

# Create minute key (YYYY-MM-DD HH:MM)
df['minute_key'] = df['timestamp_dt'].dt.strftime('%Y-%m-%d %H:%M')

# Show duplicates
duplicates = df.groupby('minute_key').size()
duplicates = duplicates[duplicates > 1]

if len(duplicates) > 0:
    print(f"\nFound duplicates in {len(duplicates)} minutes:")
    for minute, count in duplicates.items():
        print(f"  {minute}: {count} entries")

# Keep only first entry per minute
df_clean = df.drop_duplicates(subset='minute_key', keep='first')

# Remove temporary columns
df_clean = df_clean.drop(columns=['timestamp_dt', 'minute_key'])

# Save cleaned data
df_clean.to_csv(LOG_FILE, index=False)

print(f"\n✅ Cleaned data: {len(df_clean)} predictions")
print(f"   Removed: {len(df) - len(df_clean)} duplicates")
print(f"   Kept: First entry per minute")

# Show stats
with_outcomes = df_clean['actual_outcome'].notna().sum()
print(f"\n📊 Final stats:")
print(f"   Total: {len(df_clean)}")
print(f"   With outcomes: {with_outcomes}")
print(f"   Completion rate: {with_outcomes/len(df_clean)*100:.1f}%")

print("\n" + "="*70)
print("✅ DUPLICATES REMOVED - DATA CLEANED")
print("="*70)
