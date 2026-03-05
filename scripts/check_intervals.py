"""Check logging intervals"""
import pandas as pd

df = pd.read_csv('prediction_log.csv')

print("="*70)
print("LOGGING INTERVAL CHECK")
print("="*70)

if len(df) < 2:
    print("\nNeed at least 2 predictions to check intervals")
else:
    # Convert timestamps
    df['timestamp_dt'] = pd.to_datetime(df['timestamp'])
    
    # Calculate intervals between consecutive predictions
    df['interval_seconds'] = df['timestamp_dt'].diff().dt.total_seconds()
    
    # Show last 10 intervals
    print("\nLast 10 predictions with intervals:")
    recent = df.tail(10)[['timestamp', 'interval_seconds']].copy()
    
    for idx, row in recent.iterrows():
        time_str = pd.to_datetime(row['timestamp']).strftime('%H:%M:%S')
        interval = row['interval_seconds']
        
        if pd.isna(interval):
            print(f"  {time_str} - (first)")
        else:
            status = "OK" if 55 <= interval <= 65 else "SKIP" if interval > 120 else "FAST"
            print(f"  {time_str} - {interval:5.0f}s ({status})")
    
    # Statistics
    valid_intervals = df['interval_seconds'].dropna()
    if len(valid_intervals) > 0:
        avg_interval = valid_intervals.mean()
        print(f"\nAverage interval: {avg_interval:.1f} seconds")
        print(f"Min interval: {valid_intervals.min():.0f} seconds")
        print(f"Max interval: {valid_intervals.max():.0f} seconds")
        
        # Count how many are close to 60s
        good_intervals = valid_intervals[(valid_intervals >= 55) & (valid_intervals <= 65)]
        print(f"\nIntervals within 55-65s: {len(good_intervals)}/{len(valid_intervals)} ({len(good_intervals)/len(valid_intervals)*100:.1f}%)")

print("\n" + "="*70)
