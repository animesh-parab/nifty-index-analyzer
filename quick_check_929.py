import pandas as pd

df = pd.read_csv('prediction_log.csv', on_bad_lines='skip')
print(f'Total rows: {len(df)}')

# Filter for 9:29-9:39 AM
df_morning = df[df['timestamp'].str.contains('09:2') | df['timestamp'].str.contains('09:3')]
print(f'\nPredictions around 9:29-9:39 AM: {len(df_morning)}')

if len(df_morning) > 0:
    print('\n' + '='*70)
    for idx, row in df_morning.iterrows():
        print(f"Time: {row['timestamp']}")
        print(f"Direction: {row['final_direction']}")
        print(f"Confidence: {row['confidence']}%")
        print(f"Nifty: {row['entry_price']:.2f}")
        print(f"RSI: {row['rsi_14']:.1f}")
        print('-'*70)
