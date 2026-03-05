"""
Remove PCR column from prediction_log.csv
PCR APIs are unreliable - removing column to prevent bad data
"""

import pandas as pd
import os

LOG_FILE = 'prediction_log.csv'

if os.path.exists(LOG_FILE):
    # Read the CSV
    df = pd.read_csv(LOG_FILE)
    
    # Check if PCR column exists
    if 'pcr' in df.columns:
        print(f"Found PCR column in {LOG_FILE}")
        print(f"Total rows: {len(df)}")
        print(f"PCR values: {df['pcr'].unique()}")
        
        # Remove PCR column
        df = df.drop(columns=['pcr'])
        
        # Save back
        df.to_csv(LOG_FILE, index=False)
        
        print(f"✅ Removed PCR column from {LOG_FILE}")
        print(f"New columns: {list(df.columns)}")
    else:
        print(f"PCR column not found in {LOG_FILE}")
else:
    print(f"{LOG_FILE} not found")
