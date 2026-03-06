import pandas as pd
from datetime import datetime

df = pd.read_csv('prediction_log.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

today = df[df['timestamp'].dt.date == datetime(2026, 3, 6).date()]

print(f'Today March 6 predictions: {len(today)}')
if len(today) > 0:
    print(f'First: {today.iloc[0]["timestamp"]}')
    print(f'Last: {today.iloc[-1]["timestamp"]}')
else:
    print('No predictions for today yet - need to backfill from 09:30 to 15:30')
