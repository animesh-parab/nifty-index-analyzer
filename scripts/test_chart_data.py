from data_fetcher import get_candle_data
from indicators import calculate_all_indicators
from datetime import datetime
import pytz

df = get_candle_data('NIFTY')
df = calculate_all_indicators(df)

IST = pytz.timezone('Asia/Kolkata')
today = datetime.now(IST).date()

df_today = df[df.index.date == today]
print(f'Today ({today}): {len(df_today)} candles')

df_fallback = df.tail(78)
print(f'Fallback (last 78): {len(df_fallback)} candles')
print(f'Date range: {df_fallback.index[0]} to {df_fallback.index[-1]}')
print(f'Price range: {df_fallback["close"].min():.2f} to {df_fallback["close"].max():.2f}')
print(f'\nIndicators present:')
print(f'  EMA9: {"ema9" in df_fallback.columns}')
print(f'  EMA21: {"ema21" in df_fallback.columns}')
print(f'  EMA50: {"ema50" in df_fallback.columns}')
print(f'  RSI: {"rsi" in df_fallback.columns}')
print(f'  MACD: {"macd" in df_fallback.columns}')
print(f'  BB: {"bb_upper" in df_fallback.columns}')
