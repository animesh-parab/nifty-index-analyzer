"""Quick check of logging status"""
from datetime import datetime
import pytz
import pandas as pd
from config import MARKET_OPEN_HOUR, MARKET_OPEN_MIN, MARKET_CLOSE_HOUR, MARKET_CLOSE_MIN, TIMEZONE

IST = pytz.timezone(TIMEZONE)
now = datetime.now(IST)

print("="*70)
print("LOGGING STATUS CHECK")
print("="*70)
print(f"\nCurrent Time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"Hour: {now.hour}, Minute: {now.minute}")

# Check market status
market_open = (
    (now.hour > MARKET_OPEN_HOUR or (now.hour == MARKET_OPEN_HOUR and now.minute >= MARKET_OPEN_MIN)) and
    (now.hour < MARKET_CLOSE_HOUR or (now.hour == MARKET_CLOSE_HOUR and now.minute <= MARKET_CLOSE_MIN))
)

print(f"\nMarket Hours: {MARKET_OPEN_HOUR}:{MARKET_OPEN_MIN:02d} - {MARKET_CLOSE_HOUR}:{MARKET_CLOSE_MIN:02d}")
print(f"Market Status: {'OPEN ✅' if market_open else 'CLOSED ❌'}")

# Check CSV file
try:
    df = pd.read_csv('prediction_log.csv', on_bad_lines='skip')
    print(f"\nCSV File: prediction_log.csv")
    print(f"Total Predictions: {len(df)}")
    
    if len(df) > 0:
        last_timestamp = pd.to_datetime(df['timestamp'].iloc[-1])
        print(f"Last Prediction: {last_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check if recent (within last 5 minutes)
        time_diff = (now - last_timestamp.tz_localize(IST)).total_seconds() / 60
        print(f"Time Since Last: {time_diff:.1f} minutes")
        
        if time_diff < 2:
            print("Status: ✅ LOGGING ACTIVELY")
        elif time_diff < 5:
            print("Status: ⚠️ LOGGING (waiting for next cycle)")
        else:
            print("Status: ❌ NOT LOGGING (stale data)")
        
        # Show data sources
        if 'data_source' in df.columns:
            print(f"\nData Sources Used:")
            print(df['data_source'].value_counts().to_string())
    else:
        print("Status: ⚠️ No predictions yet")
        
except FileNotFoundError:
    print("\n❌ CSV file not found")
except Exception as e:
    print(f"\n❌ Error reading CSV: {e}")

print("\n" + "="*70)
