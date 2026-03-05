"""
Clean the prediction log and start fresh for clean data collection
"""

import pandas as pd
import os
from datetime import datetime

LOG_FILE = 'prediction_log.csv'
BACKUP_FILE = f'prediction_log_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

print("="*70)
print("CLEANING PREDICTION LOG FOR FRESH START")
print("="*70)

# Backup old data
if os.path.exists(LOG_FILE):
    # Create backup
    import shutil
    shutil.copy(LOG_FILE, BACKUP_FILE)
    print(f"\n✅ Backed up old data to: {BACKUP_FILE}")
    
    # Show old stats
    df_old = pd.read_csv(LOG_FILE)
    print(f"\nOld data stats:")
    print(f"  Total predictions: {len(df_old)}")
    print(f"  With outcomes: {df_old['actual_outcome'].notna().sum()}")
    print(f"  Date range: {df_old['timestamp'].min()} to {df_old['timestamp'].max()}")

# Create fresh CSV with correct structure (no PCR column)
df_new = pd.DataFrame(columns=[
    'timestamp', 'rsi_14', 'macd_value', 'macd_signal', 
    'ema_9', 'ema_21', 'ema_50', 'bb_position', 'atr_14', 
    'vix', 'hour', 'day_of_week', 'us_market_change',
    'final_direction', 'confidence', 'entry_price', 'data_source', 'actual_outcome'
])

df_new.to_csv(LOG_FILE, index=False)

print(f"\n✅ Created fresh prediction_log.csv")
print(f"   Columns: {len(df_new.columns)} (no PCR column)")
print(f"   Ready for clean data collection!")

print("\n" + "="*70)
print("READY TO START LOGGING")
print("="*70)
print("\nNext step: Run the standalone logger")
print("Command: python standalone_logger.py")
print("\nThe logger will:")
print("  ✓ Log predictions every 60 seconds (exact intervals)")
print("  ✓ Only during market hours (9:15 AM - 3:30 PM IST)")
print("  ✓ Fill outcomes after 15 minutes automatically")
print("  ✓ Use real-time data (NSE or Angel One)")
print("  ✓ Skip delayed data (yfinance)")
print("\nTarget: 300+ predictions for XGBoost training")
print("="*70)
