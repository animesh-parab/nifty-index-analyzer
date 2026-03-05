"""Check which APIs are being used in the logger"""
import pandas as pd

df = pd.read_csv('prediction_log.csv')

print("="*70)
print("API USAGE CHECK")
print("="*70)

# Check data sources
print(f"\nTotal predictions: {len(df)}")
print(f"\nData sources used:")

sources = df['data_source'].value_counts()
for source, count in sources.items():
    percentage = (count / len(df)) * 100
    print(f"  {source}: {count} ({percentage:.1f}%)")

# Show recent sources
print(f"\nLast 10 predictions:")
recent = df.tail(10)[['timestamp', 'data_source']]
for idx, row in recent.iterrows():
    time_str = pd.to_datetime(row['timestamp']).strftime('%H:%M:%S')
    print(f"  {time_str} - {row['data_source']}")

print("\n" + "="*70)
print("PRIMARY API BEING USED")
print("="*70)

primary = sources.index[0] if len(sources) > 0 else "Unknown"
print(f"\n✓ {primary}")

if "NSE" in primary:
    print("\nNSE API calls per prediction:")
    print("  1. Live Nifty price")
    print("  2. Candle data (OHLC)")
    print("  3. India VIX")
    print("  4. Global cues (US markets)")
    print("  Total: 4 API calls per minute")
elif "Angel One" in primary:
    print("\nAngel One SmartAPI calls per prediction:")
    print("  1. Live Nifty price")
    print("  2. Candle data (OHLC)")
    print("  3. India VIX")
    print("  Total: 3 API calls per minute")
elif "yfinance" in primary:
    print("\nyfinance calls per prediction:")
    print("  1. Live Nifty price")
    print("  2. Historical data")
    print("  Total: 2 API calls per minute")
    print("\n⚠️  Using delayed data (15-20 min delay)")

print("\n" + "="*70)
