"""
standalone_logger.py
Standalone prediction logger that runs independently of the dashboard

Run this in the background to ensure consistent 1-minute logging
even if the dashboard browser tab is inactive.

Usage: python standalone_logger.py
"""

import time
import logging
from datetime import datetime
import pytz
from config import TIMEZONE, MARKET_OPEN_HOUR, MARKET_OPEN_MIN, MARKET_CLOSE_HOUR, MARKET_CLOSE_MIN
from data_fetcher import get_live_nifty_price, get_candle_data, get_india_vix, get_options_chain, get_global_cues
from indicators import calculate_all_indicators, get_indicator_summary, detect_candlestick_patterns
from ai_engine_consensus import get_consensus_prediction, get_rule_based_prediction
from enhanced_prediction_engine import get_enhanced_prediction, initialize_previous_day_levels
from prediction_logger import log_prediction

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

IST = pytz.timezone(TIMEZONE)


def is_market_open():
    """Check if market is currently open"""
    now = datetime.now(IST)
    market_open = (
        (now.hour > MARKET_OPEN_HOUR or (now.hour == MARKET_OPEN_HOUR and now.minute >= MARKET_OPEN_MIN)) and
        (now.hour < MARKET_CLOSE_HOUR or (now.hour == MARKET_CLOSE_HOUR and now.minute <= MARKET_CLOSE_MIN))
    )
    return market_open and now.weekday() < 5  # Monday=0, Friday=4


def generate_and_log_prediction():
    """Generate prediction and log it"""
    try:
        logger.info("Fetching data...")
        
        # Fetch all data
        price_data = get_live_nifty_price()
        df_candles = get_candle_data()
        vix_data = get_india_vix()
        oi_data = get_options_chain()
        global_cues = get_global_cues()
        
        # Calculate indicators
        if not df_candles.empty:
            df_candles = calculate_all_indicators(df_candles)
            indicator_summary = get_indicator_summary(df_candles)
            patterns = detect_candlestick_patterns(df_candles)
            # Initialize previous day levels
            initialize_previous_day_levels(df_candles)
        else:
            logger.warning("No candle data available")
            return
        
        # Generate prediction using enhanced engine
        try:
            prediction = get_enhanced_prediction(
                price_data, indicator_summary, df_candles,
                oi_data, vix_data, {}
            )
            
            # If time filter blocks prediction, log as BLOCKED (don't skip data collection!)
            if prediction is None:
                logger.info("⏸ Time filter active - logging as BLOCKED")
                prediction = {
                    'direction': 'BLOCKED',
                    'confidence': 0,
                    'strength': 'N/A',
                    'regime': 'UNKNOWN',
                    'score': 0,
                    'model_used': 'Time Filter',
                    'generated_at': datetime.now(IST).strftime('%H:%M:%S IST')
                }
                # Continue to log — do NOT return here
                
        except Exception as e:
            logger.warning(f"Enhanced prediction failed, using rule-based: {e}")
            prediction = get_rule_based_prediction(
                indicator_summary, oi_data, vix_data, {}
            )
        
        # Get last candle for raw indicator values
        last_candle = df_candles.iloc[-1] if not df_candles.empty else {}
        
        # Prepare indicator values for logging (PCR removed - APIs unreliable)
        indicator_values = {
            'rsi_14': indicator_summary.get('RSI', {}).get('value', 0),
            'macd_value': indicator_summary.get('MACD', {}).get('value', 0),
            'macd_signal': last_candle.get('macd_signal', 0),  # Get numerical value from dataframe
            'ema_9': float(indicator_summary.get('EMA_Trend', {}).get('ema9', 0)),
            'ema_21': float(indicator_summary.get('EMA_Trend', {}).get('ema21', 0)),
            'ema_50': float(indicator_summary.get('EMA_Trend', {}).get('ema50', 0)),
            'bb_position': (last_candle.get('close', 0) - last_candle.get('bb_lower', 0)) / (last_candle.get('bb_upper', 0) - last_candle.get('bb_lower', 0)) if (last_candle.get('bb_upper', 0) - last_candle.get('bb_lower', 0)) > 0 else 0.5,
            'atr_14': indicator_summary.get('ATR', {}).get('value', 0),
            'vix': vix_data.get('vix', 15.0),
            'us_market_change': global_cues.get('S&P 500', {}).get('pct_change', 0),
            'data_source': price_data.get('source', 'Unknown')
            # PCR removed - options APIs unreliable (NSE empty, Angel One failing)
        }
        
        # Log prediction
        log_prediction(indicator_values, prediction, price_data.get("price", 0))
        
        logger.info(f"✅ Logged: {prediction.get('direction')} @ {price_data.get('price')} ({price_data.get('source')})")
        
    except Exception as e:
        logger.error(f"Error generating prediction: {e}")


def main():
    """Main loop - runs exactly every 60 seconds using scheduled timer"""
    logger.info("="*70)
    logger.info("STANDALONE PREDICTION LOGGER")
    logger.info("="*70)
    logger.info("This will log predictions every 60 seconds during market hours")
    logger.info("Press Ctrl+C to stop")
    logger.info("="*70)

    import schedule

    def job():
        """Job to run every 60 seconds"""
        now = datetime.now(IST)

        if is_market_open():
            logger.info(f"\n[{now.strftime('%H:%M:%S')}] Market OPEN - Generating prediction...")
            generate_and_log_prediction()
        else:
            logger.info(f"[{now.strftime('%H:%M:%S')}] Market CLOSED - Waiting...")

    # Schedule job to run every 60 seconds
    schedule.every(60).seconds.do(job)

    # Run first job immediately
    job()

    # Keep running scheduled jobs
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)  # Check every second for pending jobs
    except KeyboardInterrupt:
        logger.info("\n\nStopping logger...")




if __name__ == "__main__":
    main()
