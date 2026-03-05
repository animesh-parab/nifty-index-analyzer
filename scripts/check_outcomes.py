"""Check actual_outcome filling status"""
import pandas as pd

df = pd.read_csv('prediction_log.csv')
print(f'Total rows: {len(df)}')
print(f'Rows with outcome: {df["actual_outcome"].notna().sum()}')
print(f'Rows without outcome: {df["actual_outcome"].isna().sum()}')
print('\nLast 15 rows:')
print(df[['timestamp', 'entry_price', 'actual_outcome']].tail(15).to_string())
