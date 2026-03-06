"""
backfill_today_test.py
Test backfill script for any date

SAFETY: Writes ONLY to 'prediction_log_test.csv' - never touches prediction_log.csv
DATA SOURCE: Angel One or NSE only - NO yfinance
TIME RANGE: 9:30 AM to 3:00 PM (every minute)

IMPORTANT LIMITATION:
This script only works during market hours (9:15-3:30 IST)
when live candle data is available from Angel One/NSE.
Running after market close returns empty/stale candle data
resulting in SIDEWAYS/0% confidence predictions.
Use this script ONLY between 9:30 AM - 3:00 PM on trading days.
Best use case: recover gaps when logger was interrupted during market hours.

Usage:
  python backfill_today_test.py              → uses today's date
  python backfill_today_test.py 2026-03-06   → uses specific date
"""

import csv
import sys
import os
import pandas as pd
from datetime import datetime, timedelta, date
import pytz
from data_fetcher import get_candle_data, get_india_vix, get_options_chain, get_global_cues
from indicators import calculate_all_indicators, get_indicator_summary
from enhanced_prediction_engine import get_enhanced_prediction, initialize_previous_day_levels
from indicator_scoring import get_time_confidence_multiplier

IST = pytz.timezone('Asia/Kolkata')
TEST_LOG_FILE = 'prediction_log_test.csv'

def clean_field(value):
    """Clean text fields to prevent CSV corruption"""
    if isinstance(value, str):
        return value.replace('\n', ' ').replace('\r', ' ').strip()
    return value


def backfill_today_test():
    """Backfill data to test CSV"""
    
    # FIX 1: Make date dynamic (not hardcoded)
    if len(sys.argv) > 1:
        target_date = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
    else:
        target_date = date.today()
    
    print("="*60)
    print(f"BACKFILL TODAY TEST - {target_date}")
    print("="*60)
    print(f"Output file: {TEST_LOG_FILE}")
    print("Data source: Angel One or NSE only (NO yfinance)")
    print("Time range: 9:30 AM to 3:00 PM")
    print("="*60)
    
    # FIX 2: Load existing timestamps to avoid duplicates
    existing_timestamps = set()
    if os.path.exists(TEST_LOG_FILE):
        try:
            df_existing = pd.read_csv(TEST_LOG_FILE, on_bad_lines='skip')
            existing_timestamps = set(df_existing['timestamp'].values)
            print(f"✓ Found {len(existing_timestamps)} existing rows in test CSV\n")
        except:
            existing_timestamps = set()
    else:
        # Create test CSV with exact same 17 columns
        df_init = pd.DataFrame(columns=[
            'timestamp', 'rsi_14', 'macd_value', 'macd_signal', 
            'ema_9', 'ema_21', 'ema_50', 'bb_position', 'atr_14', 
            'vix', 'day_of_week', 'us_market_change',
            'final_direction', 'confidence', 'entry_price', 'data_source', 'actual_outcome'
        ])
        df_init.to_csv(TEST_LOG_FILE, index=False, quoting=csv.QUOTE_ALL)
        print(f"✓ Created {TEST_LOG_FILE} with 17 columns\n")
    
    # FIX 3: Limitation comment for static candle data
    # NOTE: Candle data is fetched ONCE and reused for all minutes.
    # This means all timestamps get the same indicator values.
    # This is a known limitation of backfill vs live logger.
    # Live logger calculates fresh indicators every 60 seconds.
    # Backfill data is approximate — use for gap recovery only.
    # Do not use backfill data for XGBoost training if live data exists.
    
    # Fetch candle data once
    print("Fetching candle data from Angel One/NSE...")
    df_candles = get_candle_data()
    
    if df_candles.empty:
        print("✗ No candle data available - cannot proceed")
        return
    
    print(f"✓ Fetched {len(df_candles)} candles")
    
    # Calculate indicators
    print("Calculating indicators...")
    df_candles = calculate_all_indicators(df_candles)
    indicator_summary = get_indicator_summary(df_candles)
    initialize_previous_day_levels(df_candles)
    print("✓ Indicators calculated\n")
    
    # Fetch VIX once
    print("Fetching VIX...")
    vix_data = get_india_vix()
    vix_value = vix_data.get('vix', 15.0)
    print(f"✓ VIX: {vix_value}\n")
    
    # Fetch options data once
    print("Fetching options chain...")
    oi_data = get_options_chain()
    print(f"✓ Options data fetched\n")
    
    # FIX 4: Get real us_market_change from global cues
    print("Fetching global cues...")
    global_cues = get_global_cues()
    us_change = global_cues.get('S&P 500', {}).get('pct_change', 0) if global_cues else 0
    print(f"✓ US market change: {us_change}\n")
    
    # Define time range using dynamic date
    start_time = datetime(target_date.year, target_date.month, target_date.day, 9, 30, 0, tzinfo=IST)
    end_time = datetime(target_date.year, target_date.month, target_date.day, 15, 0, 0, tzinfo=IST)
    
    print(f"Backfilling from {start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')}")
    print("="*60)
    
    # Reset index to make Datetime a column
    df_candles = df_candles.reset_index()
    df_candles.rename(columns={'Datetime': 'timestamp'}, inplace=True)
    df_candles['timestamp'] = pd.to_datetime(df_candles['timestamp'])
    
    predictions_added = 0
    current_time = start_time
    
    while current_time <= end_time:
        # FIX 2: Check for duplicates before processing
        if current_time.isoformat() in existing_timestamps:
            print(f"⏭  {current_time.strftime('%H:%M')} - Already exists, skipping")
            current_time += timedelta(minutes=1)
            continue
        
        # Get current price from candles (use closest timestamp)
        closest_candle = df_candles.iloc[(df_candles['timestamp'] - current_time).abs().argsort()[:1]]
        
        if len(closest_candle) > 0:
            current_price = float(closest_candle.iloc[0]['close'])
        else:
            print(f"⚠  {current_time.strftime('%H:%M:%S')} - No price data available, skipping")
            current_time += timedelta(minutes=1)
            continue
        
        # Get time confidence multiplier
        time_multiplier = get_time_confidence_multiplier(current_time.hour, current_time.minute)
        
        # Generate prediction
        try:
            prediction = get_enhanced_prediction(
                {'price': current_price, 'source': 'NSE (Test Backfill)'},
                indicator_summary,
                df_candles,
                oi_data,
                vix_data,
                {}
            )
            
            # If time filter returns None, skip this minute (pre-open or post-close)
            if time_multiplier is None:
                print(f"⏸  {current_time.strftime('%H:%M:%S')} - Time filter blocked (None), skipping")
                current_time += timedelta(minutes=1)
                continue
            
            # Apply confidence multiplier
            if prediction:
                original_confidence = prediction.get('confidence', 0)
                adjusted_confidence = int(original_confidence * time_multiplier)
                prediction['confidence'] = adjusted_confidence
            else:
                # Fallback if prediction fails
                prediction = {
                    'direction': 'SIDEWAYS',
                    'confidence': 0
                }
                
        except Exception as e:
            print(f"✗  {current_time.strftime('%H:%M:%S')} - Prediction failed: {e}")
            current_time += timedelta(minutes=1)
            continue
        
        # Get last candle for raw indicator values
        last_candle = df_candles.iloc[-1] if not df_candles.empty else {}
        
        # Prepare row data with exact 17 columns
        row_data = {
            'timestamp': current_time.isoformat(),
            'rsi_14': indicator_summary.get('RSI', {}).get('value', 0),
            'macd_value': indicator_summary.get('MACD', {}).get('value', 0),
            'macd_signal': last_candle.get('macd_signal', 0),
            'ema_9': float(indicator_summary.get('EMA_Trend', {}).get('ema9', 0)),
            'ema_21': float(indicator_summary.get('EMA_Trend', {}).get('ema21', 0)),
            'ema_50': float(indicator_summary.get('EMA_Trend', {}).get('ema50', 0)),
            'bb_position': (last_candle.get('close', 0) - last_candle.get('bb_lower', 0)) / (last_candle.get('bb_upper', 0) - last_candle.get('bb_lower', 0)) if (last_candle.get('bb_upper', 0) - last_candle.get('bb_lower', 0)) > 0 else 0.5,
            'atr_14': indicator_summary.get('ATR', {}).get('value', 0),
            'vix': vix_value,
            'day_of_week': current_time.weekday(),
            'us_market_change': us_change,
            'final_direction': clean_field(prediction.get('direction', 'SIDEWAYS')),
            'confidence': prediction.get('confidence', 0),
            'entry_price': current_price,
            'data_source': 'NSE (Test Backfill)',
            'actual_outcome': ''
        }
        
        # Append to test CSV with proper quoting
        df_entry = pd.DataFrame([row_data])
        df_entry.to_csv(TEST_LOG_FILE, mode='a', header=False, index=False, quoting=csv.QUOTE_ALL)
        
        print(f"✅ {current_time.strftime('%H:%M:%S')} - {prediction.get('direction')} ({prediction.get('confidence')}%) at {current_price:.2f} [multiplier={time_multiplier}]")
        
        predictions_added += 1
        current_time += timedelta(minutes=1)
    
    print("\n" + "="*60)
    print(f"BACKFILL COMPLETE")
    print(f"Predictions added: {predictions_added}")
    print(f"Output file: {TEST_LOG_FILE}")
    print("="*60)
    
    # Verify test CSV
    print("\nVerifying test CSV...")
    df_test = pd.read_csv(TEST_LOG_FILE)
    print(f"Total rows: {len(df_test)}")
    print(f"Columns: {len(df_test.columns)}")
    print(f"\nDirection counts:")
    print(df_test['final_direction'].value_counts())
    print(f"\nFirst 3 rows:")
    print(df_test[['timestamp', 'final_direction', 'confidence', 'entry_price']].head(3))
    print(f"\nLast 3 rows:")
    print(df_test[['timestamp', 'final_direction', 'confidence', 'entry_price']].tail(3))


if __name__ == "__main__":
    backfill_today_test()
