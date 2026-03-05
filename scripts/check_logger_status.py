"""Check if logger is working and collecting data"""
import pandas as pd
import os
from datetime import datetime

LOG_FILE = 'prediction_log.csv'

print("="*70)
print("LOGGER STATUS CHECK")
print("="*70)

# Check if CSV exists
if not os.path.exists(LOG_FILE):
    print("\n❌ prediction_log.csv not found!")
    print("   Logger may not have started yet")
else:
    df = pd.read_csv(LOG_FILE)
    
    print(f"\n✅ CSV file exists")
    print(f"   Total predictions: {len(df)}")
    
    if len(df) == 0:
        print("\n⏳ No predictions logged yet")
        print("   Logger may be waiting for market hours or just started")
    else:
        print(f"\n✅ Data is being collected!")
        print(f"   First prediction: {df['timestamp'].iloc[0]}")
        print(f"   Last prediction: {df['timestamp'].iloc[-1]}")
        print(f"   With outcomes: {df['actual_outcome'].notna().sum()}")
        
        # Show last prediction
        last = df.iloc[-1]
        print(f"\n   Last logged:")
        print(f"   - Time: {last['timestamp']}")
        print(f"   - Direction: {last['final_direction']}")
        print(f"   - Price: {last['entry_price']}")
        print(f"   - Source: {last['data_source']}")

# Check market hours
from config import TIMEZONE, MARKET_OPEN_HOUR, MARKET_OPEN_MIN, MARKET_CLOSE_HOUR, MARKET_CLOSE_MIN
import pytz

IST = pytz.timezone(TIMEZONE)
now = datetime.now(IST)
market_open = (
    (now.hour > MARKET_OPEN_HOUR or (now.hour == MARKET_OPEN_HOUR and now.minute >= MARKET_OPEN_MIN)) and
    (now.hour < MARKET_CLOSE_HOUR or (now.hour == MARKET_CLOSE_HOUR and now.minute <= MARKET_CLOSE_MIN))
)
is_weekday = now.weekday() < 5

print(f"\n📅 Current time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"   Market open: {'✅ YES' if market_open and is_weekday else '❌ NO'}")

if not market_open or not is_weekday:
    print(f"\n   ℹ️  Logger will wait until market opens")
    print(f"   Market hours: 9:15 AM - 3:30 PM IST, Mon-Fri")

print("\n" + "="*70)
