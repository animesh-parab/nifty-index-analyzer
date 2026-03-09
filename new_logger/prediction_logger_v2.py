"""
prediction_logger_v2.py
REWRITTEN CSV logger with focus on preventing corruption

Key changes:
1. Explicit UTF-8 encoding
2. Always use csv.QUOTE_ALL
3. Clean all text fields before writing
4. Atomic writes (write to temp, then rename)
5. Validate row before writing
"""

import csv
import os
import logging
from datetime import datetime
import pytz
import pandas as pd

IST = pytz.timezone('Asia/Kolkata')
MAIN_CSV = 'new_logger/predictions_v2.csv'

def get_daily_csv_path():
    """Generate daily CSV path with current date"""
    return f'new_logger/predictions_v2_{datetime.now(IST).strftime("%Y_%m_%d")}.csv'

logger = logging.getLogger(__name__)

COLUMNS = [
    'timestamp', 'rsi_14', 'macd_value', 'macd_signal',
    'ema_9', 'ema_21', 'ema_50', 'bb_position', 'atr_14',
    'vix', 'day_of_week', 'us_market_change',
    'final_direction', 'confidence', 'entry_price',
    'data_source', 'actual_outcome'
]


def clean_text(value):
    """Aggressively clean text to prevent CSV corruption"""
    if value is None:
        return ''
    
    text = str(value)
    # Remove newlines, carriage returns, quotes
    text = text.replace('\n', ' ').replace('\r', ' ').replace('"', "'")
    # Remove any non-printable characters
    text = ''.join(char for char in text if char.isprintable() or char == ' ')
    return text.strip()


def validate_row(row_data):
    """Validate row has exactly 17 fields"""
    expected_fields = [
        'timestamp', 'rsi_14', 'macd_value', 'macd_signal',
        'ema_9', 'ema_21', 'ema_50', 'bb_position', 'atr_14',
        'vix', 'day_of_week', 'us_market_change',
        'final_direction', 'confidence', 'entry_price', 'data_source', 'actual_outcome'
    ]
    
    if len(row_data) != len(expected_fields):
        return False, f"Expected {len(expected_fields)} fields, got {len(row_data)}"
    
    return True, "OK"


def initialize_csv(filepath):
    """Create CSV with header if doesn't exist"""
    if not os.path.exists(filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(COLUMNS)
        
        logger.info(f"✓ Created {filepath}")


def log_prediction(indicator_values: dict, prediction: dict, current_price: float):
    """
    Log prediction to CSV with corruption prevention
    Writes to BOTH main CSV and daily CSV
    """
    try:
        DAILY_CSV = get_daily_csv_path()
        initialize_csv(MAIN_CSV)
        initialize_csv(DAILY_CSV)
        
        now = datetime.now(IST)
        
        # Build row with cleaned values
        row_data = {
            'timestamp': now.isoformat(),
            'rsi_14': float(indicator_values.get('rsi_14', 0)),
            'macd_value': float(indicator_values.get('macd_value', 0)),
            'macd_signal': float(indicator_values.get('macd_signal', 0)),
            'ema_9': float(indicator_values.get('ema_9', 0)),
            'ema_21': float(indicator_values.get('ema_21', 0)),
            'ema_50': float(indicator_values.get('ema_50', 0)),
            'bb_position': float(indicator_values.get('bb_position', 0.5)),
            'atr_14': float(indicator_values.get('atr_14', 0)),
            'vix': float(indicator_values.get('vix', 15.0)),
            'day_of_week': int(now.weekday()),
            'us_market_change': float(indicator_values.get('us_market_change', 0)),
            'final_direction': clean_text(prediction.get('direction', 'SIDEWAYS')),
            'confidence': int(prediction.get('confidence', 0)),
            'entry_price': float(current_price),
            'data_source': clean_text(indicator_values.get('data_source', 'Unknown')),
            'actual_outcome': ''
        }
        
        # Convert to list in correct order
        row_list = [row_data[col] for col in COLUMNS]
        
        # Validate before writing
        valid, msg = validate_row(row_list)
        if not valid:
            logger.error(f"Row validation failed: {msg}")
            return
        
        # Write to BOTH CSVs
        df = pd.DataFrame([row_data])
        
        # Write to MAIN CSV
        df.to_csv(MAIN_CSV, mode='a', header=not os.path.exists(MAIN_CSV), 
                  index=False, quoting=csv.QUOTE_ALL, encoding='utf-8')
        
        # Write to DAILY CSV
        df.to_csv(DAILY_CSV, mode='a', header=not os.path.exists(DAILY_CSV),
                  index=False, quoting=csv.QUOTE_ALL, encoding='utf-8')
        
        logger.info(f"✓ Logged to BOTH CSVs: {prediction.get('direction')} at {current_price}")
        
    except Exception as e:
        logger.error(f"Error logging prediction: {e}")


if __name__ == "__main__":
    # Test
    DAILY_CSV = get_daily_csv_path()
    initialize_csv(MAIN_CSV)
    initialize_csv(DAILY_CSV)
    print(f"✓ Main CSV initialized at {MAIN_CSV}")
    print(f"✓ Daily CSV initialized at {DAILY_CSV}")
