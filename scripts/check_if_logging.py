"""Quick check if logger is working"""
import pandas as pd
from datetime import datetime

df = pd.read_csv('prediction_log.csv')
print(f"Total predictions: {len(df)}")

if len(df) > 0:
    last_time = df.iloc[-1]['timestamp']
    print(f"Last prediction: {last_time}")
    
    # Check if recent (within last 2 minutes)
    last_dt = pd.to_datetime(last_time)
    now = datetime.now()
    diff_seconds = (now - last_dt.replace(tzinfo=None)).total_seconds()
    
    if diff_seconds < 120:
        print(f"✅ Logger is working! (last log {diff_seconds:.0f}s ago)")
    else:
        print(f"⚠️  Logger may not be running (last log {diff_seconds/60:.1f} min ago)")
else:
    print("⚠️  No predictions yet")
