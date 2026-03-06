"""
Check current market conditions for trade setup potential
"""

from data_fetcher import get_candle_data
from indicators import calculate_all_indicators
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

print("="*70)
print("CURRENT MARKET CONDITIONS")
print("="*70)
print(f"Time: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}")
print("="*70)

# Fetch data
df = get_candle_data('NIFTY')
df = calculate_all_indicators(df)

if df.empty or len(df) < 20:
    print("❌ Insufficient data")
    exit(1)

# Get last 20 candles for range
last_20 = df.tail(20)
current = df.iloc[-1]

# Calculate key metrics
recent_high = last_20['High'].max()
recent_low = last_20['Low'].min()
range_size = recent_high - recent_low
current_price = current['Close']
position_in_range = (current_price - recent_low) / range_size if range_size > 0 else 0.5

# Get RSI
rsi = current.get('RSI', 50)
prev_rsi = df.iloc[-2].get('RSI', 50) if len(df) > 1 else rsi
rsi_rising = rsi > prev_rsi

# Get ATR
atr = current.get('ATR', 0)

# Distance to support/resistance
distance_to_support = current_price - recent_low
distance_to_resistance = recent_high - current_price

# Time check
now = datetime.now(IST)
time_minutes = now.hour * 60 + now.minute
in_trading_hours = (600 <= time_minutes <= 720) or (810 <= time_minutes <= 870)

print(f"\n📊 PRICE ACTION")
print(f"Current Price: ₹{current_price:,.2f}")
print(f"Recent High (20 candles): ₹{recent_high:,.2f}")
print(f"Recent Low (20 candles): ₹{recent_low:,.2f}")
print(f"Range Size: {range_size:.2f} points")
print(f"Position in Range: {position_in_range:.1%}")

print(f"\n📈 TECHNICAL INDICATORS")
print(f"RSI: {rsi:.1f} (Previous: {prev_rsi:.1f}) - {'Rising ✓' if rsi_rising else 'Falling ✗'}")
print(f"ATR: {atr:.2f}")

print(f"\n📏 DISTANCES")
print(f"Distance to Support: {distance_to_support:.2f} points")
print(f"Distance to Resistance: {distance_to_resistance:.2f} points")

print(f"\n⏰ TIME FILTER")
print(f"Current Time: {now.strftime('%H:%M:%S')}")
print(f"In Trading Hours (10:00-12:00 or 1:30-2:30): {'✓ YES' if in_trading_hours else '✗ NO'}")

print(f"\n🎯 CALL SETUP POTENTIAL")
print(f"Position < 0.25: {'✓' if position_in_range < 0.25 else '✗'} ({position_in_range:.1%})")
print(f"RSI < 45: {'✓' if rsi < 45 else '✗'} ({rsi:.1f})")
print(f"RSI Rising: {'✓' if rsi_rising else '✗'}")
print(f"Distance to Support < 25: {'✓' if distance_to_support < 25 else '✗'} ({distance_to_support:.2f})")
print(f"Time Filter: {'✓' if in_trading_hours else '✗'}")

call_conditions_met = sum([
    position_in_range < 0.25,
    rsi < 45,
    rsi_rising,
    distance_to_support < 25,
    in_trading_hours
])
print(f"\nCALL Conditions Met: {call_conditions_met}/5 (need 7/7 with R:R and candles)")

print(f"\n🎯 PUT SETUP POTENTIAL")
print(f"Position > 0.7: {'✓' if position_in_range > 0.7 else '✗'} ({position_in_range:.1%})")
print(f"RSI > 60: {'✓' if rsi > 60 else '✗'} ({rsi:.1f})")
print(f"Distance to Resistance < 5: {'✓' if distance_to_resistance < 5 else '✗'} ({distance_to_resistance:.2f})")
print(f"Distance to Support > 100: {'✓' if distance_to_support > 100 else '✗'} ({distance_to_support:.2f})")
print(f"Time Filter: {'✓' if in_trading_hours else '✗'}")

put_conditions_met = sum([
    position_in_range > 0.7,
    rsi > 60,
    distance_to_resistance < 5,
    distance_to_support > 100,
    in_trading_hours
])
print(f"\nPUT Conditions Met: {put_conditions_met}/5 (need 7/7 with rally and R:R)")

print("\n" + "="*70)
if call_conditions_met >= 4:
    print("🟢 CALL SETUP FORMING - Watch closely!")
elif put_conditions_met >= 4:
    print("🔴 PUT SETUP FORMING - Watch closely!")
else:
    print("⚪ NO SETUP FORMING - Wait for better conditions")
print("="*70)
