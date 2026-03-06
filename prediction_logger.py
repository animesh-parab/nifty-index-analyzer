"""
prediction_logger.py
Logs predictions and actual outcomes for XGBoost training

Logs every prediction with indicators and actual outcome 15 minutes later.
"""

import pandas as pd
import csv
import os
from datetime import datetime, timedelta
import threading
import time
import yfinance as yf
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LOG_FILE = 'prediction_log.csv'
OUTCOME_DELAY_MINUTES = 60  # Updated to 60-min lookback on March 4 2026 (was 15 minutes)

# Track last log time to prevent duplicates within same minute
_last_log_time = None
_log_lock = threading.Lock()


def clean_field(value):
    """
    Clean text fields to prevent CSV corruption.
    Removes newlines, carriage returns, and extra whitespace.
    """
    if isinstance(value, str):
        value = value.replace('\n', ' ')
        value = value.replace('\r', ' ')
        value = ' '.join(value.split())
    return value

# Initialize CSV if it doesn't exist
if not os.path.exists(LOG_FILE):
    df = pd.DataFrame(columns=[
        'timestamp', 'rsi_14', 'macd_value', 'macd_signal', 
        'ema_9', 'ema_21', 'ema_50', 'bb_position', 'atr_14', 
        'vix', 'hour', 'day_of_week', 'us_market_change',
        'final_direction', 'confidence', 'entry_price', 'data_source', 'actual_outcome'
    ])
    df.to_csv(LOG_FILE, index=False, quoting=csv.QUOTE_ALL)
    logger.info(f"Created new prediction log: {LOG_FILE}")


def log_prediction(indicator_values: dict, prediction: dict, current_price: float):
    """
    Log a prediction with all indicator values.
    Only logs if data source is real-time (NSE or Angel One).
    Rate limited to once per minute to prevent duplicates.
    
    Args:
        indicator_values: Dict with all indicator values (must include 'data_source')
        prediction: Prediction dict with direction and confidence
        current_price: Current Nifty price for outcome calculation
    """
    global _last_log_time
    
    try:
        # Check data source - only log real-time data
        data_source = indicator_values.get('data_source', 'Unknown')
        
        if 'yfinance' in data_source.lower():
            logger.info(f"Skipping log - using delayed data source: {data_source}")
            return
        
        now = datetime.now()
        
        # Rate limiting: Only log once per minute
        with _log_lock:
            if _last_log_time:
                time_since_last = (now - _last_log_time).total_seconds()
                if time_since_last < 55:  # Less than 55 seconds since last log
                    logger.debug(f"Skipping log - only {time_since_last:.0f}s since last log (need 55s)")
                    return
            
            _last_log_time = now
        
        # Prepare log entry (PCR removed - APIs unreliable)
        log_entry = {
            'timestamp': now.isoformat(),
            'rsi_14': indicator_values.get('rsi_14', 0),
            'macd_value': indicator_values.get('macd_value', 0),
            'macd_signal': indicator_values.get('macd_signal', 0),
            'ema_9': indicator_values.get('ema_9', 0),
            'ema_21': indicator_values.get('ema_21', 0),
            'ema_50': indicator_values.get('ema_50', 0),
            'bb_position': indicator_values.get('bb_position', 0),
            'atr_14': indicator_values.get('atr_14', 0),
            'vix': indicator_values.get('vix', 15.0),
            'hour': now.hour,
            'day_of_week': now.weekday(),
            'us_market_change': indicator_values.get('us_market_change', 0),
            'final_direction': clean_field(prediction.get('direction', 'SIDEWAYS')),
            'confidence': prediction.get('confidence', 0),
            'entry_price': current_price,
            'data_source': clean_field(data_source),
            'actual_outcome': None  # Will be filled later
        }
        
        # Append to CSV with proper quoting to prevent corruption
        df = pd.DataFrame([log_entry])
        df.to_csv(LOG_FILE, mode='a', header=False, index=False, quoting=csv.QUOTE_ALL)
        
        # Schedule outcome check in background thread
        thread = threading.Thread(
            target=_check_outcome_later,
            args=(now, current_price),
            daemon=True
        )
        thread.start()
        
        logger.info(f"Logged prediction: {prediction.get('direction')} at {current_price} (source: {data_source})")
        
    except Exception as e:
        logger.error(f"Error logging prediction: {e}")


def _check_outcome_later(prediction_time: datetime, entry_price: float):
    """
    Wait 60 minutes, then check actual outcome based on MAXIMUM price movement.
    Uses highest/lowest prices in the 60-minute window to capture intraday spikes.
    Runs in background thread.
    Updated to max movement logic on March 4 2026
    """
    try:
        # Wait 60 minutes
        logger.info(f"Scheduled outcome check for {prediction_time.strftime('%H:%M:%S')} in 60 minutes")
        time.sleep(OUTCOME_DELAY_MINUTES * 60)

        # Fetch 1-minute candles for the entire day
        ticker = yf.Ticker("^NSEI")
        current_data = ticker.history(period="1d", interval="1m")

        if current_data.empty:
            logger.warning(f"Could not fetch outcome price for {prediction_time.strftime('%H:%M:%S')}")
            return

        # Get all prices in the 60-minute window after prediction
        # Find candles after prediction time
        prediction_time_naive = prediction_time.replace(tzinfo=None)
        
        # Filter candles in the 60-minute window
        window_end = prediction_time_naive + timedelta(minutes=60)
        mask = (current_data.index >= prediction_time_naive) & (current_data.index <= window_end)
        window_data = current_data[mask]

        if window_data.empty:
            logger.warning(f"No data in 60-minute window for {prediction_time.strftime('%H:%M:%S')}")
            return

        # Calculate maximum price movements in the window
        highest_price = window_data['High'].max()
        lowest_price = window_data['Low'].min()

        # Calculate max up and down moves
        max_up_move = (highest_price - entry_price) / entry_price
        max_down_move = (entry_price - lowest_price) / entry_price

        # Determine outcome based on maximum movement
        # If max_up_move > 0.3% AND greater than max_down_move → UP
        # If max_down_move > 0.3% AND greater than max_up_move → DOWN
        # Otherwise → SIDEWAYS
        
        THRESHOLD = 0.003  # 0.3%
        
        if max_up_move > THRESHOLD and max_up_move > max_down_move:
            outcome = 1  # UP
            logger.info(f"Outcome UP: max_up={max_up_move*100:.2f}%, max_down={max_down_move*100:.2f}%")
        elif max_down_move > THRESHOLD and max_down_move > max_up_move:
            outcome = -1  # DOWN
            logger.info(f"Outcome DOWN: max_up={max_up_move*100:.2f}%, max_down={max_down_move*100:.2f}%")
        else:
            outcome = 0  # SIDEWAYS
            logger.info(f"Outcome SIDEWAYS: max_up={max_up_move*100:.2f}%, max_down={max_down_move*100:.2f}%")

        # Update the log entry with thread-safe file access
        with _log_lock:
            df = pd.read_csv(LOG_FILE)

            # Find the entry (match timestamp)
            mask = df['timestamp'] == prediction_time.isoformat()

            if mask.any():
                df.loc[mask, 'actual_outcome'] = outcome
                df.to_csv(LOG_FILE, index=False, quoting=csv.QUOTE_ALL)
                logger.info(f"✅ Updated outcome for {prediction_time.strftime('%H:%M:%S')}: {outcome}")
            else:
                logger.warning(f"Could not find prediction entry for {prediction_time.strftime('%H:%M:%S')}")

    except Exception as e:
        logger.error(f"Error checking outcome for {prediction_time.strftime('%H:%M:%S')}: {e}")



def get_log_stats():
    """Get statistics about logged predictions."""
    try:
        if not os.path.exists(LOG_FILE):
            return {
                'total': 0,
                'with_outcome': 0,
                'ready_for_training': False
            }
        
        df = pd.read_csv(LOG_FILE)
        total = len(df)
        with_outcome = df['actual_outcome'].notna().sum()
        
        return {
            'total': total,
            'with_outcome': with_outcome,
            'ready_for_training': with_outcome >= 300,
            'accuracy': None  # Can calculate if needed
        }
        
    except Exception as e:
        logger.error(f"Error getting log stats: {e}")
        return {'total': 0, 'with_outcome': 0, 'ready_for_training': False}


def extract_indicator_values(df_candles: pd.DataFrame, oi_data: dict, 
                            vix_data: dict, global_cues: dict) -> dict:
    """
    Extract raw indicator values for logging/prediction.
    PCR removed temporarily due to unreliable options APIs.
    
    Args:
        df_candles: DataFrame with calculated indicators
        oi_data: Options chain data (not used currently)
        vix_data: VIX data
        global_cues: Global market data
    
    Returns:
        Dict with all indicator values
    """
    try:
        if df_candles.empty:
            return {}
        
        last = df_candles.iloc[-1]
        
        # Calculate BB position (0-1, where 0.5 is middle)
        bb_upper = last.get('bb_upper', 0)
        bb_lower = last.get('bb_lower', 0)
        close = last.get('close', 0)
        
        if bb_upper > bb_lower:
            bb_position = (close - bb_lower) / (bb_upper - bb_lower)
        else:
            bb_position = 0.5
        
        # Get US market change (average of major indices)
        us_change = 0
        if global_cues:
            us_indices = ['Dow Jones', 'S&P 500', 'Nasdaq']
            changes = [global_cues.get(idx, {}).get('pct_change', 0) 
                      for idx in us_indices if idx in global_cues]
            if changes:
                us_change = sum(changes) / len(changes)
        
        return {
            'rsi_14': last.get('rsi', 50),
            'macd_value': last.get('macd', 0),
            'macd_signal': last.get('macd_signal', 0),
            'ema_9': last.get('ema9', 0),
            'ema_21': last.get('ema21', 0),
            'ema_50': last.get('ema50', 0),
            'bb_position': bb_position,
            'atr_14': last.get('atr', 0),
            'vix': vix_data.get('vix', 15.0),
            'us_market_change': us_change
            # PCR removed - options APIs unreliable (NSE empty, Angel One failing)
        }
        
    except Exception as e:
        logger.error(f"Error extracting indicator values: {e}")
        return {}


if __name__ == "__main__":
    # Test
    print("Prediction Logger Test")
    print("="*50)
    
    stats = get_log_stats()
    print(f"Total predictions logged: {stats['total']}")
    print(f"With outcomes: {stats['with_outcome']}")
    print(f"Ready for training: {stats['ready_for_training']}")
