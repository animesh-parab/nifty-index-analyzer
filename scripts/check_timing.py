import pandas as pd
from datetime import datetime

df = pd.read_csv('prediction_log.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Get recent predictions (after 10:00 AM)
recent = df[df['timestamp'] > '2026-03-02 10:00:00'].copy()
recent['time'] = recent['timestamp'].dt.strftime('%H:%M:%S')

print("="*70)
print("PREDICTION TIMING ANALYSIS")
print("="*70)
print("\nRecent predictions (after 10:00 AM):")
for idx, row in recent.iterrows():
    print(f"  {row['time']}")

print(f"\nTotal predictions today (after 10:00): {len(recent)}")

if len(recent) > 1:
    # Calculate time gaps
    recent['time_diff'] = recent['timestamp'].diff().dt.total_seconds()
    print("\nTime gaps between predictions (seconds):")
    for idx, row in recent[1:].iterrows():
        print(f"  {row['time']}: {row['time_diff']:.0f}s gap")
    
    avg_gap = recent['time_diff'].mean()
    print(f"\nAverage gap: {avg_gap:.0f} seconds")
    print(f"Expected: 60 seconds (1 minute)")
    
    if avg_gap > 70:
        print("\n⚠️ WARNING: Gaps larger than expected")
        print("Possible causes:")
        print("  - Dashboard not refreshing every minute")
        print("  - Data fetch failures (falling back to yfinance)")
        print("  - Browser/tab not active (Streamlit pauses when inactive)")
    elif avg_gap < 50:
        print("\n✅ Logging faster than expected (good!)")
    else:
        print("\n✅ Timing looks good")

print("="*70)
