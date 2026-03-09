"""Check which APIs are being used"""
import pandas as pd

df = pd.read_csv('prediction_log.csv', on_bad_lines='skip')

print("="*70)
print("DATA SOURCE CHECK")
print("="*70)

print(f"\nTotal predictions: {len(df)}")
print(f"\nData sources used:")

sources = df['data_source'].value_counts()
for source, count in sources.items():
    percentage = (count / len(df)) * 100
    print(f"  {source}: {count} ({percentage:.1f}%)")

print(f"\nLast 10 predictions:")
recent = df.tail(10)[['timestamp', 'data_source']]
for idx, row in recent.iterrows():
    time_str = pd.to_datetime(row['timestamp']).strftime('%H:%M:%S')
    print(f"  {time_str} - {row['data_source']}")

print("\n" + "="*70)
