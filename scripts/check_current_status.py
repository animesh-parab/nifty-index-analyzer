"""Check current CSV status"""
import pandas as pd
from datetime import datetime

df = pd.read_csv('prediction_log.csv', on_bad_lines='skip')

print("="*70)
print("CURRENT CSV STATUS")
print("="*70)

print(f"\nTotal predictions: {len(df)}")
print(f"With outcomes: {df['actual_outcome'].notna().sum()}")
print(f"Without outcomes: {df['actual_outcome'].isna().sum()}")

if len(df) > 0:
    # Get last prediction
    last = df.iloc[-1]
    last_time = pd.to_datetime(last['timestamp'])
    
    print(f"\nLast prediction:")
    print(f"  Time: {last_time.strftime('%H:%M:%S')}")
    print(f"  Direction: {last['final_direction']}")
    print(f"  Price: {last['entry_price']}")
    print(f"  Outcome: {last['actual_outcome'] if pd.notna(last['actual_outcome']) else 'Pending'}")
    
    # Check if logger is still running
    now = datetime.now()
    diff_seconds = (now - last_time.replace(tzinfo=None)).total_seconds()
    
    print(f"\nTime since last log: {diff_seconds:.0f} seconds")
    
    if diff_seconds < 90:
        print("Status: Logger is RUNNING")
    else:
        print("Status: Logger may have STOPPED")
        print(f"Expected new prediction by now (last was {diff_seconds/60:.1f} min ago)")
    
    # Show last 5 predictions
    print(f"\nLast 5 predictions:")
    recent = df.tail(5)[['timestamp', 'final_direction', 'entry_price', 'actual_outcome']]
    for idx, row in recent.iterrows():
        time_str = pd.to_datetime(row['timestamp']).strftime('%H:%M:%S')
        outcome = row['actual_outcome']
        outcome_str = 'Pending' if pd.isna(outcome) else f"{int(outcome)}"
        print(f"  {time_str} - {row['final_direction']:10s} @ {row['entry_price']:.2f} - Outcome: {outcome_str}")

print("\n" + "="*70)
print("To see updates in Excel: Close and reopen the file")
print("="*70)
