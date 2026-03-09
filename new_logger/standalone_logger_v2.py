"""
standalone_logger_v2.py
REWRITTEN standalone logger - cleaner, simpler, more robust

Run: python new_logger/standalone_logger_v2.py
Output: new_logger/predictions_clean.csv
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import logging
from datetime import datetime
import pytz
import schedule

from config import TIMEZONE, MARKET_OPEN_HOUR, MARKET_OPEN_MIN, MARKET_CLOSE_HOUR, MARKET_CLOSE_MIN
from data_fetcher import get_live_nifty_price, get_candle_data, get_india_vix, get_options_chain, get_global_cues
from indicators import calculate_all_indicators, get_indicator_summary
from enhanced_prediction_engine import get_enhanced_prediction, initialize_previous_day_levels
from indicator_scoring import get_time_confidence_multiplier

# Import new logger
from new_logger.prediction_logger_v2 import log_prediction

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

IST = pytz.timezone(TIMEZONE)


def is_market_open():
    """Check if market is currently open"""
    now = datetime.now(IST)
    current_minutes = now.hour * 60 + now.minute
    open_minutes = MARKET_OPEN_HOUR * 60 + MARKET_OPEN_MIN
    close_minutes = MARKET_CLOSE_HOUR * 60 + MARKET_CLOSE_MIN
    return open_minutes <= current_minutes <= close_minutes and now.weekday() < 5


def generate_and_log_prediction(time_multiplier=1.0):
    """Generate prediction and log it"""
    try:
        logger.info("Fetching data...")
        
        # Fetch data
        price_data = get_live_nifty_price()
        df_candles = get_candle_data()
        vix_data = get_india_vix()
        oi_data = get_options_chain()
        global_cues = get_global_cues()
        
        # Calculate indicators
        if df_candles.empty:
            logger.warning("No candle data available")
            return
        
        df_candles = calculate_all_indicators(df_candles)
        indicator_summary = get_indicator_summary(df_candles)
        initialize_previous_day_levels(df_candles)
        
        # Generate prediction
        prediction = get_enhanced_prediction(
            price_data, indicator_summary, df_candles,
            oi_data, vix_data, {}
        )
        
        # Apply time multiplier to confidence BEFORE any blocking checks
        if prediction and prediction.get('direction') != 'BLOCKED':
            original = prediction.get('confidence', 0)
            prediction['confidence'] = int(original * time_multiplier)
        
        # Get last candle for indicators
        last_candle = df_candles.iloc[-1] if not df_candles.empty else {}
        
        # Prepare indicator values
        indicator_values = {
            'rsi_14': indicator_summary.get('RSI', {}).get('value', 0),
            'macd_value': indicator_summary.get('MACD', {}).get('value', 0),
            'macd_signal': last_candle.get('macd_signal', 0),
            'ema_9': float(indicator_summary.get('EMA_Trend', {}).get('ema9', 0)),
            'ema_21': float(indicator_summary.get('EMA_Trend', {}).get('ema21', 0)),
            'ema_50': float(indicator_summary.get('EMA_Trend', {}).get('ema50', 0)),
            'bb_position': (last_candle.get('close', 0) - last_candle.get('bb_lower', 0)) / (last_candle.get('bb_upper', 0) - last_candle.get('bb_lower', 0)) if (last_candle.get('bb_upper', 0) - last_candle.get('bb_lower', 0)) > 0 else 0.5,
            'atr_14': indicator_summary.get('ATR', {}).get('value', 0),
            'vix': vix_data.get('vix', 15.0),
            'us_market_change': global_cues.get('S&P 500', {}).get('pct_change', 0),
            'data_source': price_data.get('source', 'Unknown')
        }
        
        # Log prediction
        log_prediction(indicator_values, prediction, price_data.get("price", 0))
        
        logger.info(f"✅ Logged: {prediction.get('direction')} @ {price_data.get('price')} ({price_data.get('source')})")
        
    except Exception as e:
        logger.error(f"Error generating prediction: {e}")


def main():
    """Main loop"""
    logger.info("="*70)
    logger.info("STANDALONE LOGGER V2 (CLEAN)")
    logger.info("="*70)
    logger.info("Main CSV: new_logger/predictions_v2.csv")
    logger.info("Daily CSV: new_logger/predictions_v2_YYYY_MM_DD.csv")
    logger.info("Logs every 60 seconds during market hours")
    logger.info("Press Ctrl+C to stop")
    logger.info("="*70)

    def job():
        """Job to run every 60 seconds"""
        now = datetime.now(IST)
        
        if not is_market_open():
            logger.info(f"[{now.strftime('%H:%M:%S')}] Market CLOSED - Waiting...")
            return
        
        multiplier = get_time_confidence_multiplier(now.hour, now.minute)
        
        if multiplier is None:
            logger.info(f"[{now.strftime('%H:%M:%S')}] Time filter blocked - skipping")
            return
        
        logger.info(f"\n[{now.strftime('%H:%M:%S')}] Generating prediction [multiplier={multiplier}]...")
        generate_and_log_prediction(multiplier)

    # Schedule job every 60 seconds
    schedule.every(60).seconds.do(job)
    
    # Run first job immediately
    job()
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n\nStopping logger...")


if __name__ == "__main__":
    main()
