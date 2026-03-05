"""Check when outcomes should start appearing"""
import pandas as pd
from datetime import datetime, timedelta

df = pd.read_csv('prediction_log.csv')

print("="*70)
print("OUTCOME TIMING CHECK")
print("="*70)

if len(df) == 0:
    print("\nNo predictions yet")
else:
    # Convert timestamps
    df['timestamp_dt'] = pd.to_datetime(df['timestamp'])
    now = datetime.now()
    
    # Find first prediction
    first_pred = df.iloc[0]
    first_time = first_pred['timestamp_dt'].replace(tzinfo=None)
    first_outcome_time = first_time + timedelta(minutes=15)
    
    print(f"\nFirst prediction: {first_time.strftime('%H:%M:%S')}")
    print(f"First outcome due: {first_outcome_time.strftime('%H:%M:%S')}")
    
    # Check if we're past that time
    if now >= first_outcome_time:
        print(f"Status: Should be filling now!")
        
        # Check how many should have outcomes
        should_have = df[df['timestamp_dt'] <= (now - timedelta(minutes=15))]
        actually_have = df[df['actual_outcome'].notna()]
        
        print(f"\nPredictions >15 min old: {len(should_have)}")
        print(f"Predictions with outcomes: {len(actually_have)}")
        
        if len(actually_have) < len(should_have):
            print(f"\nMissing outcomes: {len(should_have) - len(actually_have)}")
            print("Outcomes are filled by background threads (may take a moment)")
    else:
        wait_seconds = (first_outcome_time - now).total_seconds()
        wait_minutes = wait_seconds / 60
        print(f"Status: Wait {wait_minutes:.1f} more minutes")
        print(f"Current time: {now.strftime('%H:%M:%S')}")
    
    # Show recent predictions
    print(f"\nRecent predictions:")
    recent = df.tail(5)[['timestamp', 'final_direction', 'entry_price', 'actual_outcome']]
    for idx, row in recent.iterrows():
        outcome = row['actual_outcome']
        outcome_str = 'Pending' if pd.isna(outcome) else f"{int(outcome)}"
        print(f"  {row['timestamp'][11:19]} - {row['final_direction']:10s} @ {row['entry_price']:.2f} - Outcome: {outcome_str}")

print("\n" + "="*70)
