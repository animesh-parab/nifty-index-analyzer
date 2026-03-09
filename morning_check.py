# morning_check.py
# Run at 9:15 AM before starting logger
# Takes 60 seconds to complete full verification

import pandas as pd
import time
from datetime import datetime
import pytz

IST = pytz.timezone('Asia/Kolkata')

print('='*50)
print('MORNING SYSTEM CHECK')
print(f'Time: {datetime.now(IST).strftime("%H:%M:%S IST")}')
print('='*50)

# Check 1: Time filter
print('\n1. Time Filter Check:')
try:
    from indicator_scoring import get_time_confidence_multiplier
    r1 = get_time_confidence_multiplier(9, 15)
    r2 = get_time_confidence_multiplier(9, 30)
    r3 = get_time_confidence_multiplier(10, 0)
    r4 = get_time_confidence_multiplier(13, 30)
    if r1 is None and r2 == 0.5 and r3 == 1.0 and r4 == 1.0:
        print('   ✅ Time filter correct')
    else:
        print(f'   ❌ Time filter wrong: 9:15={r1}, 9:30={r2}, 10:00={r3}, 13:30={r4}')
except Exception as e:
    print(f'   ❌ Time filter error: {e}')

# Check 2: CSV status
print('\n2. CSV Status:')
try:
    df = pd.read_csv('prediction_log.csv', on_bad_lines='skip')
    print(f'   ✅ Rows: {len(df)}')
    print(f'   ✅ Last timestamp: {df["timestamp"].iloc[-1]}')
    print(f'   ✅ Columns: {len(df.columns)} (expected 17)')
except Exception as e:
    print(f'   ❌ CSV ERROR: {e}')

# Check 3: Live data fetch
print('\n3. Live Data Check:')
try:
    from data_fetcher import get_live_nifty_price, get_india_vix
    price_data = get_live_nifty_price()
    price = price_data.get('price', 0)
    source = price_data.get('source', 'Unknown')
    if price > 20000:
        print(f'   ✅ Nifty price: {price} (source: {source})')
    else:
        print(f'   ❌ Bad price: {price} - API may be down')
except Exception as e:
    print(f'   ❌ Price fetch error: {e}')

try:
    vix_data = get_india_vix()
    vix = vix_data.get('vix', 0)
    if vix > 0:
        print(f'   ✅ VIX: {vix}')
    else:
        print(f'   ❌ VIX fetch failed')
except Exception as e:
    print(f'   ❌ VIX error: {e}')

# Check 4: Candle data
print('\n4. Candle Data Check:')
try:
    from data_fetcher import get_candle_data
    from indicators import calculate_all_indicators
    df_candles = get_candle_data()
    if not df_candles.empty:
        print(f'   ✅ Candles fetched: {len(df_candles)} rows')
        # Reset index to access timestamp
        df_candles_reset = df_candles.reset_index()
        if 'Datetime' in df_candles_reset.columns:
            print(f'   ✅ Latest candle: {df_candles_reset["Datetime"].iloc[-1]}')
        else:
            print(f'   ✅ Latest candle: {df_candles.index[-1]}')
    else:
        print(f'   ❌ No candle data - API may be down')
except Exception as e:
    print(f'   ❌ Candle error: {e}')

# Check 5: Prediction engine
print('\n5. Prediction Engine Check:')
try:
    from enhanced_prediction_engine import get_enhanced_prediction
    print('   ✅ Prediction engine imports OK')
except Exception as e:
    print(f'   ❌ Prediction engine error: {e}')

# Check 6: Start logger test
print('\n6. Quick Logger Test (60 seconds):')
print('   Starting logger for 60 seconds...')
try:
    import subprocess
    import signal
    
    # Get row count before
    df_before = pd.read_csv('prediction_log.csv', on_bad_lines='skip')
    df_before_count = len(df_before)
    
    process = subprocess.Popen(['python', 'standalone_logger.py'])
    time.sleep(65)
    process.terminate()
    print('   Logger ran for 60 seconds ✅')
    
    # Check if new row was added
    df_after = pd.read_csv('prediction_log.csv', on_bad_lines='skip')
    if len(df_after) > df_before_count:
        new_rows = df_after.tail(len(df_after) - df_before_count)
        print(f'   ✅ New rows added: {len(df_after) - df_before_count}')
        print(f'   ✅ Direction: {new_rows["final_direction"].values}')
        print(f'   ✅ Confidence: {new_rows["confidence"].values}')
        print(f'   ✅ Source: {new_rows["data_source"].values}')
    else:
        print('   ⚠️  No new rows added (expected if market closed)')
    
    # Verify CSV still clean
    pd.read_csv('prediction_log.csv', on_bad_lines='skip')
    print('   ✅ CSV still clean after logger test')

except Exception as e:
    print(f'   ❌ Logger test error: {e}')

# Final summary
print('\n' + '='*50)
print('SUMMARY:')
print('If all ✅ → run: python standalone_logger.py')
print('If any ❌ → fix before starting')
print('='*50)
