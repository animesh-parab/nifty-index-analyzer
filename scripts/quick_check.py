import pandas as pd
df = pd.read_csv('prediction_log.csv')
print(f'Total: {len(df)}')
print(f'Last: {df.iloc[-1]["timestamp"]}')
