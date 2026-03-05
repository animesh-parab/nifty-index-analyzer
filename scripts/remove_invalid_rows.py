"""
Remove rows with invalid data (EMA = 0) from prediction log
These are typically logged outside market hours with missing candle data
"""

import pandas as pd
from datetime import datetime

LOG_FILE = "prediction_log.csv"
BACKUP_FILE = f"backups/prediction_log_before_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

def remove_invalid_rows():
    """Remove rows where EMAs are 0 (invalid data)"""
    
    # Read CSV
    df = pd.read_csv(LOG_FILE)
    print(f"Total predictions: {len(df)}")
    
    # Find invalid rows (any EMA = 0)
    invalid_mask = (df['ema_9'] == 0) | (df['ema_21'] == 0) | (df['ema_50'] == 0)
    invalid_rows = df[invalid_mask]
    
    print(f"\nInvalid rows found: {len(invalid_rows)}")
    if len(invalid_rows) > 0:
        print("\nInvalid rows (EMA = 0):")
        print(invalid_rows[['timestamp', 'ema_9', 'ema_21', 'ema_50', 'entry_price']])
        
        # Backup before removing
        df.to_csv(BACKUP_FILE, index=False)
        print(f"\n✅ Backup saved: {BACKUP_FILE}")
        
        # Remove invalid rows
        df_clean = df[~invalid_mask]
        
        # Save cleaned data
        df_clean.to_csv(LOG_FILE, index=False)
        
        print(f"\n✅ Removed {len(invalid_rows)} invalid rows")
        print(f"Clean predictions: {len(df_clean)}")
        
        # Show outcome stats
        with_outcomes = df_clean['actual_outcome'].notna().sum()
        print(f"With outcomes: {with_outcomes}")
        print(f"Without outcomes: {len(df_clean) - with_outcomes}")
    else:
        print("\n✅ No invalid rows found - data is clean!")

if __name__ == "__main__":
    remove_invalid_rows()
