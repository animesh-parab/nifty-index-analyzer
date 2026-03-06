"""
Backfill missing predictions from 9:30 AM to current time
Fetches historical 1-minute candle data and generates predictions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import time

from data_fetcher import get_candle_data, get_india_vix, get_options_chain
from indicators import calculate_all_indicators
from enhanced_prediction_engine import get_enhanced_prediction, initialize_previous_day_levels
from prediction_logger import log_prediction

IST = pytz.timezone("Asia/Kolkata")
LOG_FILE = 'prediction_log.csv'

def backfill_missing_predictions(start_time_str: str, end_time_str: str):
    """
    Backfill predictions for missing time period
    
    Args:
        start_time_str: Start time in HH:MM format (e.g., "09:30")
        end_time_str: End time in HH:MM format (e.g., "10:16")
    """
    print(f"\n{'='*60}")
    print(f"BACKFILLING PREDICTIONS: {start_time_str} to {end_time_str}")
    print(f"{'='*60}\n")
    
    # Parse times
    today = datetime.now(IST).date()
    start_hour, start_min = map(int, start_time_str.split(':'))
    end_hour, end_min = map(int, end_time_str.split(':'))
    
    start_time = datetime(today.year, today.month, today.day, start_hour, start_min, tzinfo=IST)
    end_time = datetime(today.year, today.month, today.day, end_hour, end_min, tzinfo=IST)
    
    print(f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S IST')}")
    print(f"End: {end_time.strftime('%Y-%m-%d %H:%M:%S IST')}")
    print(f"Duration: {(end_time - start_time).total_seconds() / 60:.0f} minutes\n")
    
    # Fetch candle data
    print("Fetching candle data...")
    df_candles = get_candle_data("NIFTY")
    
    if df_candles.empty:
        print("❌ ERROR: Could not fetch candle data")
        return
    
    # Calculate indicators
    print("Calculating indicators...")
    df_candles = calculate_all_indicators(df_candles)
    
    # Initialize previous day levels
    initialize_previous_day_levels(df_candles)
    
    # Fetch VIX and options data once
    print("Fetching VIX and options data...")
    vix_data = get_india_vix()
    oi_data = get_options_chain()
    
    print(f"\nVIX: {vix_data.get('vix', 'N/A')}")
    print(f"PCR: {oi_data.get('pcr', 'N/A')}")
    print(f"Max Pain: {oi_data.get('max_pain', 'N/A')}\n")
    
    # Read existing log to avoid duplicates
    existing_df = pd.read_csv(LOG_FILE)
    existing_timestamps = set(existing_df['timestamp'].values)
    
    # Generate predictions for each minute in the range
    predictions_added = 0
    predictions_skipped = 0
    
    current_time = start_time
    while current_time <= end_time:
        timestamp_str = current_time.isoformat()
        
        # Skip if already exists
        if timestamp_str in existing_timestamps:
            print(f"⏭️  {current_time.strftime('%H:%M:%S')} - Already exists, skipping")
            predictions_skipped += 1
            current_time += timedelta(minutes=1)
            continue
        
        # Get candles up to this time
        candles_up_to_time = df_candles[df_candles.index <= current_time]
        
        if len(candles_up_to_time) < 20:
            print(f"⚠️  {current_time.strftime('%H:%M:%S')} - Insufficient data (<20 candles), skipping")
            current_time += timedelta(minutes=1)
            continue
        
        # Get current price
        last_candle = candles_up_to_time.iloc[-1]
        current_price = last_candle['close']
        
        # Get indicator summary
        from indicators import get_indicator_summary
        indicator_summary = get_indicator_summary(candles_up_to_time)
        
        # Generate prediction
        try:
            prediction = get_enhanced_prediction(
                {'price': current_price, 'source': 'Backfill'},
                indicator_summary,
                candles_up_to_time,
                oi_data,
                vix_data,
                {}  # No news sentiment for backfill
            )
            
            if prediction is None or prediction.get('direction') == 'BLOCKED':
                print(f"⏭️  {current_time.strftime('%H:%M:%S')} - Time filter blocked, skipping")
                current_time += timedelta(minutes=1)
                continue
            
            # Prepare indicator values for logging
            indicator_values = {
                'rsi_14': indicator_summary.get('RSI', {}).get('value', 0),
                'macd_value': indicator_summary.get('MACD', {}).get('value', 0),
                'macd_signal': last_candle.get('macd_signal', 0),
                'ema_9': indicator_summary.get('EMA_Trend', {}).get('ema_9', 0),
                'ema_21': indicator_summary.get('EMA_Trend', {}).get('ema_21', 0),
                'ema_50': indicator_summary.get('EMA_Trend', {}).get('ema_50', 0),
                'bb_position': (last_candle.get('close', 0) - last_candle.get('bb_lower', 0)) / (last_candle.get('bb_upper', 0) - last_candle.get('bb_lower', 0)) if (last_candle.get('bb_upper', 0) - last_candle.get('bb_lower', 0)) > 0 else 0.5,
                'atr_14': indicator_summary.get('ATR', {}).get('value', 0),
                'vix': vix_data.get('vix', 15.0),
                'us_market_change': 0,  # Not available for backfill
                'data_source': 'NSE (Backfill)'
            }
            
            # Create log entry manually (don't use log_prediction to avoid outcome thread)
            log_entry = {
                'timestamp': timestamp_str,
                'rsi_14': indicator_values['rsi_14'],
                'macd_value': indicator_values['macd_value'],
                'macd_signal': indicator_values['macd_signal'],
                'ema_9': indicator_values['ema_9'],
                'ema_21': indicator_values['ema_21'],
                'ema_50': indicator_values['ema_50'],
                'bb_position': indicator_values['bb_position'],
                'atr_14': indicator_values['atr_14'],
                'vix': indicator_values['vix'],
                'hour': current_time.hour,
                'day_of_week': current_time.weekday(),
                'us_market_change': 0,
                'final_direction': prediction.get('direction', 'SIDEWAYS'),
                'confidence': prediction.get('confidence', 0),
                'entry_price': current_price,
                'data_source': 'NSE (Backfill)',
                'actual_outcome': None  # Will be filled by backfill_outcomes.py
            }
            
            # Append to CSV
            df_entry = pd.DataFrame([log_entry])
            df_entry.to_csv(LOG_FILE, mode='a', header=False, index=False)
            
            print(f"✅ {current_time.strftime('%H:%M:%S')} - {prediction.get('direction')} ({prediction.get('confidence')}%) at {current_price:.2f}")
            predictions_added += 1
            
        except Exception as e:
            print(f"❌ {current_time.strftime('%H:%M:%S')} - Error: {str(e)}")
        
        # Move to next minute
        current_time += timedelta(minutes=1)
        
        # Small delay to avoid overwhelming the system
        time.sleep(0.1)
    
    print(f"\n{'='*60}")
    print(f"BACKFILL COMPLETE")
    print(f"{'='*60}")
    print(f"✅ Predictions added: {predictions_added}")
    print(f"⏭️  Predictions skipped (already exist): {predictions_skipped}")
    print(f"\nNext step: Run backfill_outcomes.py to fill actual outcomes")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python backfill_missing_predictions.py START_TIME END_TIME")
        print("Example: python backfill_missing_predictions.py 09:30 10:16")
        sys.exit(1)
    
    start_time = sys.argv[1]
    end_time = sys.argv[2]
    
    backfill_missing_predictions(start_time, end_time)
