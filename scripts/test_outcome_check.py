"""Test if outcome checking is working"""
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf

# Get predictions that should have outcomes by now (older than 15 minutes)
df = pd.read_csv('prediction_log.csv')

# Filter predictions without outcomes that are older than 15 minutes
now = datetime.now()
df['timestamp_dt'] = pd.to_datetime(df['timestamp'])
df['age_minutes'] = (now - df['timestamp_dt']).dt.total_seconds() / 60

# Find predictions that should have outcomes
should_have_outcome = df[(df['actual_outcome'].isna()) & (df['age_minutes'] > 15)]

print(f"Total predictions: {len(df)}")
print(f"Predictions with outcomes: {df['actual_outcome'].notna().sum()}")
print(f"Predictions without outcomes: {df['actual_outcome'].isna().sum()}")
print(f"Predictions that SHOULD have outcomes (>15 min old): {len(should_have_outcome)}")

if len(should_have_outcome) > 0:
    print("\nTesting outcome check for oldest prediction without outcome...")
    oldest = should_have_outcome.iloc[0]
    print(f"Timestamp: {oldest['timestamp']}")
    print(f"Entry price: {oldest['entry_price']}")
    print(f"Age: {oldest['age_minutes']:.1f} minutes")
    
    # Try to fetch current price
    try:
        ticker = yf.Ticker("^NSEI")
        current_data = ticker.history(period="1d", interval="1m")
        
        if not current_data.empty:
            exit_price = current_data['Close'].iloc[-1]
            price_change_pct = ((exit_price - oldest['entry_price']) / oldest['entry_price']) * 100
            
            if price_change_pct > 0.1:
                outcome = 1  # UP
            elif price_change_pct < -0.1:
                outcome = -1  # DOWN
            else:
                outcome = 0  # SIDEWAYS
            
            print(f"\n✅ Outcome check successful!")
            print(f"Exit price: {exit_price}")
            print(f"Price change: {price_change_pct:.2f}%")
            print(f"Outcome: {outcome}")
        else:
            print("\n❌ yfinance returned empty data")
    except Exception as e:
        print(f"\n❌ Error fetching price: {e}")
else:
    print("\n✅ All predictions have outcomes!")
