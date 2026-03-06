"""
Fetch Nifty spot prices at specific times
"""

from data_fetcher import get_candle_data
from indicators import calculate_all_indicators
from datetime import datetime, time
import pytz

IST = pytz.timezone("Asia/Kolkata")

print("="*70)
print("NIFTY SPOT PRICES - MARCH 6, 2026")
print("="*70)

# Fetch candle data
print("\nFetching candle data...")
df = get_candle_data('NIFTY')

if df.empty:
    print("❌ ERROR: Could not fetch candle data")
    exit(1)

print(f"✓ Fetched {len(df)} candles")

# Filter for today only
today = datetime.now(IST).date()
df_today = df[df.index.date == today]

if df_today.empty:
    print("❌ ERROR: No data for today")
    exit(1)

print(f"✓ Today's candles: {len(df_today)}")

# Get high of the day
high_of_day = df_today['High'].max()
high_time = df_today[df_today['High'] == high_of_day].index[0]

print("\n" + "="*70)
print("HIGH OF THE DAY")
print("="*70)
print(f"High: ₹{high_of_day:,.2f}")
print(f"Time: {high_time.strftime('%H:%M:%S IST')}")

# Find prices at specific times
target_times = [
    (9, 29, "9:29 AM (Call Given)"),
    (10, 32, "10:32 AM (Exit Called)")
]

print("\n" + "="*70)
print("PRICES AT SPECIFIC TIMES")
print("="*70)

for hour, minute, label in target_times:
    # Find candle closest to this time
    target_time = datetime(today.year, today.month, today.day, hour, minute, tzinfo=IST)
    
    # Find candles within 5 minutes of target
    time_diff = abs((df_today.index - target_time).total_seconds())
    closest_idx = time_diff.argmin()
    closest_candle = df_today.iloc[closest_idx]
    closest_time = df_today.index[closest_idx]
    
    print(f"\n{label}")
    print(f"Time: {closest_time.strftime('%H:%M:%S IST')}")
    print(f"Open: ₹{closest_candle['Open']:,.2f}")
    print(f"High: ₹{closest_candle['High']:,.2f}")
    print(f"Low: ₹{closest_candle['Low']:,.2f}")
    print(f"Close: ₹{closest_candle['Close']:,.2f}")
    print(f"Spot (Close): ₹{closest_candle['Close']:,.2f}")

# Calculate profit if trade was taken
print("\n" + "="*70)
print("TRADE ANALYSIS")
print("="*70)

# Get 9:29 price
target_929 = datetime(today.year, today.month, today.day, 9, 29, tzinfo=IST)
time_diff_929 = abs((df_today.index - target_929).total_seconds())
idx_929 = time_diff_929.argmin()
price_929 = df_today.iloc[idx_929]['Close']

# Get 10:32 price
target_1032 = datetime(today.year, today.month, today.day, 10, 32, tzinfo=IST)
time_diff_1032 = abs((df_today.index - target_1032).total_seconds())
idx_1032 = time_diff_1032.argmin()
price_1032 = df_today.iloc[idx_1032]['Close']

profit = price_1032 - price_929
profit_pct = (profit / price_929) * 100

print(f"Entry (9:29 AM): ₹{price_929:,.2f}")
print(f"Exit (10:32 AM): ₹{price_1032:,.2f}")
print(f"Profit: {profit:+,.2f} points ({profit_pct:+.2f}%)")

if profit > 0:
    print(f"\n✅ PROFITABLE TRADE: +{profit:.2f} points")
else:
    print(f"\n❌ LOSS: {profit:.2f} points")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"High of Day: ₹{high_of_day:,.2f} at {high_time.strftime('%H:%M:%S')}")
print(f"Entry Price: ₹{price_929:,.2f}")
print(f"Exit Price: ₹{price_1032:,.2f}")
print(f"Points Gained: {profit:+,.2f}")
print(f"Percentage: {profit_pct:+.2f}%")
print("="*70)
