"""
Remove predictions logged outside market hours (before 9:15 AM or after 3:30 PM)
"""

import pandas as pd
from datetime import datetime

LOG_FILE = "prediction_log.csv"
BACKUP_FILE = f"backups/prediction_log_before_hours_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

def remove_outside_hours():
    """Remove rows logged outside market hours"""
    
    # Read CSV
    df = pd.read_csv(LOG_FILE)
    print(f"Total predictions: {len(df)}")
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    df['minute'] = df['timestamp'].dt.minute
    
    # Market hours: 9:15 AM - 3:30 PM
    outside_hours = (
        (df['hour'] < 9) | 
        (df['hour'] > 15) | 
        ((df['hour'] == 9) & (df['minute'] < 15)) |
        ((df['hour'] == 15) & (df['minute'] > 30))
    )
    
    outside_rows = df[outside_hours]
    
    print(f"\nRows outside market hours: {len(outside_rows)}")
    if len(outside_rows) > 0:
        print("\nOutside market hours:")
        print(outside_rows[['timestamp', 'entry_price', 'final_direction']])
        
        # Backup before removing
        df.to_csv(BACKUP_FILE, index=False)
        print(f"\n✅ Backup saved: {BACKUP_FILE}")
        
        # Remove outside hours rows
        df_clean = df[~outside_hours]
        
        # Drop helper columns
        df_clean = df_clean.drop(['hour', 'minute'], axis=1)
        
        # Save cleaned data
        df_clean.to_csv(LOG_FILE, index=False)
        
        print(f"\n✅ Removed {len(outside_rows)} rows outside market hours")
        print(f"Clean predictions: {len(df_clean)}")
        
        # Show outcome stats
        with_outcomes = df_clean['actual_outcome'].notna().sum()
        print(f"With outcomes: {with_outcomes}")
        print(f"Without outcomes: {len(df_clean) - with_outcomes}")
    else:
        print("\n✅ No rows outside market hours - data is clean!")

if __name__ == "__main__":
    remove_outside_hours()
