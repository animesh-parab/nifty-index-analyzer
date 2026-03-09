"""
Backfill missing actual_outcome values for predictions older than 15 minutes
"""

import pandas as pd
from datetime import datetime
import yfinance as yf
import time

LOG_FILE = 'prediction_log.csv'

def backfill_outcomes():
    """Backfill all missing outcomes for predictions older than 15 minutes"""
    
    # Read the log
    df = pd.read_csv(LOG_FILE)
    
    # Convert timestamp to datetime (handle both old and new formats)
    df['timestamp_dt'] = pd.to_datetime(df['timestamp'], format='mixed', utc=True)
    
    # Calculate age in minutes
    now = pd.Timestamp.now(tz='UTC')
    df['age_minutes'] = (now - df['timestamp_dt']).dt.total_seconds() / 60
    
    # Find predictions that need outcomes (>15 min old, no outcome yet)
    needs_outcome = df[(df['actual_outcome'].isna()) & (df['age_minutes'] > 15)]
    
    print(f"Total predictions: {len(df)}")
    print(f"Predictions with outcomes: {df['actual_outcome'].notna().sum()}")
    print(f"Predictions needing outcomes: {len(needs_outcome)}")
    
    if len(needs_outcome) == 0:
        print("\n✅ All predictions have outcomes!")
        return
    
    print(f"\nBackfilling {len(needs_outcome)} outcomes...")
    
    # Get current price once
    ticker = yf.Ticker("^NSEI")
    current_data = ticker.history(period="1d", interval="1m")
    
    if current_data.empty:
        print("❌ Could not fetch current price from yfinance")
        return
    
    exit_price = current_data['Close'].iloc[-1]
    print(f"Current Nifty price: {exit_price}")
    
    # Update each prediction
    updated = 0
    for idx, row in needs_outcome.iterrows():
        entry_price = row['entry_price']
        price_change_pct = ((exit_price - entry_price) / entry_price) * 100
        
        if price_change_pct > 0.1:
            outcome = 1  # UP
        elif price_change_pct < -0.1:
            outcome = -1  # DOWN
        else:
            outcome = 0  # SIDEWAYS
        
        df.at[idx, 'actual_outcome'] = outcome
        updated += 1
        
        if updated % 10 == 0:
            print(f"  Updated {updated}/{len(needs_outcome)}...")
    
    # Remove temporary columns
    df = df.drop(columns=['timestamp_dt', 'age_minutes'])
    
    # Save back to CSV
    df.to_csv(LOG_FILE, index=False)
    
    print(f"\n✅ Backfilled {updated} outcomes!")
    print(f"Total predictions with outcomes: {df['actual_outcome'].notna().sum()}")
    
    # Show outcome distribution
    print(f"\nOutcome distribution:")
    print(f"  UP (+1): {(df['actual_outcome'] == 1).sum()}")
    print(f"  SIDEWAYS (0): {(df['actual_outcome'] == 0).sum()}")
    print(f"  DOWN (-1): {(df['actual_outcome'] == -1).sum()}")


if __name__ == "__main__":
    backfill_outcomes()
