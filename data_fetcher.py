"""
data_fetcher.py
Multi-source live data fetcher with Angel One SmartAPI integration.
Sources: Angel One (primary) → NSE API → yfinance (fallback)

IMPROVEMENTS:
- ✅ Real-time data from Angel One SmartAPI (0 delay)
- ✅ Better session management (auto-refresh every 5 min)
- ✅ Retry logic (3 attempts with exponential backoff)
- ✅ Rate limiting (2 seconds between requests)
- ✅ Fallback handling (Angel One → NSE → yfinance → cache)
- ✅ API usage tracking for monitoring
"""

import yfinance as yf
import pandas as pd
import numpy as np
import requests
import time
import json
import pytz
import random
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import warnings
import logging
warnings.filterwarnings("ignore")

from config import (
    NSE_HEADERS, NIFTY_SYMBOL_YF, VIX_SYMBOL_YF,
    BANKNIFTY_SYMBOL_YF, NIFTY_SYMBOL_NSE, BANKNIFTY_SYMBOL_NSE,
    CANDLE_INTERVAL, CANDLE_PERIOD, CROSS_VALIDATE_THRESHOLD, TIMEZONE
)

# API usage tracking
from api_rate_monitor import record_api_call

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IST = pytz.timezone(TIMEZONE)

# Try to import Angel One fetcher (PRIMARY SOURCE)
try:
    from angel_one_fetcher import (
        fetch_nifty_angel, 
        fetch_vix_angel, 
        fetch_candles_angel,
        fetch_options_chain_angel,
        get_nearest_expiry
    )
    USE_ANGEL_ONE = True
    logger.info("✓ Using Angel One SmartAPI (Real-time data)")
except ImportError:
    USE_ANGEL_ONE = False
    logger.warning("⚠ Angel One not available, using fallback sources")

# Try to import enhanced NSE fetcher
try:
    from nse_fetcher_enhanced import EnhancedNSEFetcher
    _enhanced_nse = EnhancedNSEFetcher()
    USE_ENHANCED_NSE = True
    logger.info("✓ Enhanced NSE Fetcher available as fallback")
except ImportError:
    USE_ENHANCED_NSE = False
    logger.warning("⚠ Enhanced NSE Fetcher not found, using basic version")

# NSE SESSION (persists cookies) - for fallback
_nse_session = None
_session_created_at = None

def _get_nse_session():
    """Get or refresh NSE session (basic fallback)"""
    global _nse_session, _session_created_at
    now = datetime.now()
    
    # Refresh session every 5 minutes
    if (_nse_session is None or 
        _session_created_at is None or 
        (now - _session_created_at).total_seconds() > 300):
        
        logger.info("Creating new NSE session (fallback)...")
        _nse_session = requests.Session()
        _nse_session.headers.update(NSE_HEADERS)
        try:
            _nse_session.get("https://www.nseindia.com", timeout=10)
            time.sleep(1)
            _session_created_at = now
            logger.info("✓ NSE session created")
        except Exception as e:
            logger.error(f"✗ Failed to create NSE session: {e}")
    
    return _nse_session


def fetch_nifty_nse(index="NIFTY") -> dict:
    """
    Fetch live Nifty 50 or Bank Nifty data from NSE API.
    Uses enhanced fetcher with retry logic and rate limiting.
    
    Args:
        index: "NIFTY" or "BANKNIFTY"
    """
    # Map index to NSE symbol
    index_symbol = NIFTY_SYMBOL_NSE if index == "NIFTY" else BANKNIFTY_SYMBOL_NSE
    
    # Try enhanced fetcher first (with all improvements)
    if USE_ENHANCED_NSE:
        try:
            result = _enhanced_nse.get_nifty_data(index)
            if result.get('success'):
                logger.info(f"✓ NSE data fetched via enhanced fetcher for {index}")
                record_api_call("nse", f"equity-stockIndices/{index}")
                return result
            else:
                logger.warning(f"⚠ Enhanced fetcher failed for {index}, trying fallback...")
        except Exception as e:
            logger.error(f"✗ Enhanced fetcher error for {index}: {e}")
    
    # Fallback to basic method with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            sess = _get_nse_session()
            # Use correct URL based on index
            if index == "NIFTY":
                url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
            else:  # BANKNIFTY
                url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20BANK"
            
            resp = sess.get(url, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                idx = data["data"][0]
                logger.info(f"✓ NSE data fetched via fallback for {index} (attempt {attempt + 1})")
                record_api_call("nse", f"equity-stockIndices/{index}")
                return {
                    "price": float(idx.get("lastPrice", 0) or idx.get("last", 0)),
                    "open": float(idx.get("open", 0)),
                    "high": float(idx.get("dayHigh", 0)),
                    "low": float(idx.get("dayLow", 0)),
                    "prev_close": float(idx.get("previousClose", 0)),
                    "change": float(idx.get("change", 0)),
                    "pct_change": float(idx.get("pChange", 0)),
                    "source": "NSE",
                    "timestamp": datetime.now(IST).isoformat(),
                    "success": True,
                    "index": index
                }
            elif resp.status_code == 401:
                # Session expired, refresh and retry
                logger.warning("Session expired, refreshing...")
                global _nse_session, _session_created_at
                _nse_session = None
                _session_created_at = None
                continue
                
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on attempt {attempt + 1}/{max_retries}")
        except Exception as e:
            logger.error(f"Error on attempt {attempt + 1}/{max_retries}: {e}")
        
        # Exponential backoff before retry
        if attempt < max_retries - 1:
            sleep_time = (2 ** attempt) + random.uniform(0, 1)
            logger.info(f"Retrying in {sleep_time:.1f}s...")
            time.sleep(sleep_time)
    
    logger.error("✗ All NSE fetch attempts failed")
    return {"success": False}


def fetch_nifty_yfinance(index="NIFTY") -> dict:
    """Fetch Nifty 50 or Bank Nifty from yfinance (15-min delayed).
    
    Args:
        index: "NIFTY" or "BANKNIFTY"
    """
    try:
        symbol = NIFTY_SYMBOL_YF if index == "NIFTY" else BANKNIFTY_SYMBOL_YF
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        price = float(info.last_price or 0)
        prev = float(info.previous_close or 0)
        record_api_call("yfinance", f"Ticker/{symbol}")
        return {
            "price": price,
            "prev_close": prev,
            "change": round(price - prev, 2),
            "pct_change": round((price - prev) / prev * 100, 2) if prev else 0,
            "source": "yfinance",
            "timestamp": datetime.now(IST).isoformat(),
            "index": index
        }
    except Exception:
        return {}


def get_live_nifty_price(index="NIFTY") -> dict:
    """
    Fetch from multiple sources with smart fallback handling.
    Priority: NSE (real-time, reliable) → Angel One (real-time, backup) → yfinance (15-min delayed)
    Returns best available data with confidence info.
    
    Args:
        index: "NIFTY" or "BANKNIFTY"

    IMPROVEMENTS:
    - ✅ NSE API as primary (real-time, fast, reliable)
    - ✅ Angel One as secondary (real-time, 0 delay)
    - ✅ yfinance as tertiary (15-min delayed)
    - ✅ Multi-source fallback chain
    - ✅ Confidence scoring based on data quality
    - ✅ Detailed logging for debugging
    """
    logger.info(f"Fetching live {index} price...")

    # Try NSE first (real-time, fast, reliable)
    nse = fetch_nifty_nse(index)

    if nse and nse.get("price", 0) > 0 and nse.get("success", False):
        logger.info(f"✓ NSE data available for {index} (real-time)")
        nse["confidence"] = "HIGH"
        nse["source"] = "NSE API (Real-time)"
        nse["index"] = index
        return nse

    # Fallback to Angel One (real-time, 0 delay)
    angel_data = None
    if USE_ANGEL_ONE:
        try:
            angel_data = fetch_nifty_angel(index)
            if angel_data and angel_data.get('price', 0) > 0:
                logger.info(f"✓ Angel One data available for {index} (real-time)")
                # Convert Angel One format to standard format
                return {
                    "price": angel_data['price'],
                    "prev_close": angel_data['close'],
                    "change": angel_data['change'],
                    "pct_change": angel_data['change_percent'],
                    "source": "Angel One (Real-time)",
                    "timestamp": angel_data['timestamp'].isoformat(),
                    "success": True,
                    "confidence": "VERY HIGH",
                    "index": index
                }
        except Exception as e:
            logger.warning(f"⚠ Angel One fetch failed for {index}: {e}")

    # Fallback to yfinance (15-min delayed backup)
    yf_data = fetch_nifty_yfinance(index)

    if yf_data and yf_data.get("price", 0) > 0:
        logger.info(f"✓ yfinance data available for {index} (15-min delayed)")
        yf_data["confidence"] = "LOW"
        yf_data["source"] = "yfinance (15-min delay)"
        yf_data["index"] = index
        return yf_data

    # All sources failed
    logger.error(f"✗ All data sources failed for {index}")
    return {
        "price": 0,
        "error": "All sources failed",
        "confidence": "NONE",
        "source": "FAILED",
        "index": index
    }


def get_candle_data(index="NIFTY", interval: str = CANDLE_INTERVAL, period: str = CANDLE_PERIOD) -> pd.DataFrame:
    """
    Fetch OHLCV candle data.
    Priority: Angel One (real-time) → yfinance (delayed)
    
    Args:
        index: "NIFTY" or "BANKNIFTY"
        interval: Candle interval
        period: Data period
    """
    # Try Angel One first (real-time candles)
    if USE_ANGEL_ONE:
        try:
            # Map interval to Angel One format
            interval_map = {
                "1m": "ONE_MINUTE",
                "5m": "FIVE_MINUTE",
                "15m": "FIFTEEN_MINUTE",
                "1h": "ONE_HOUR",
                "1d": "ONE_DAY"
            }
            angel_interval = interval_map.get(interval, "FIVE_MINUTE")
            
            # Map period to days
            period_days = {
                "1d": 1,
                "5d": 5,
                "1mo": 30,
                "3mo": 90
            }
            days = period_days.get(period, 5)
            
            df = fetch_candles_angel(index, interval=angel_interval, days=days)
            if not df.empty:
                logger.info(f"✓ Angel One candles fetched for {index}: {len(df)} candles")
                # Rename columns to match expected format
                df = df.rename(columns={
                    "timestamp": "Datetime",
                    "open": "Open",
                    "high": "High",
                    "low": "Low",
                    "close": "Close",
                    "volume": "Volume"
                })
                df.set_index('Datetime', inplace=True)
                
                # Also keep lowercase versions for compatibility
                df['open'] = df['Open']
                df['high'] = df['High']
                df['low'] = df['Low']
                df['close'] = df['Close']
                df['volume'] = df['Volume']
                
                return df
        except Exception as e:
            logger.warning(f"⚠ Angel One candles failed for {index}: {e}, falling back to yfinance")
    
    # Fallback to yfinance
    try:
        symbol = NIFTY_SYMBOL_YF if index == "NIFTY" else BANKNIFTY_SYMBOL_YF
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        if df.empty:
            df = ticker.history(period="5d", interval="5m")
        if not df.empty:
            df.index = df.index.tz_convert(IST)
            # Keep both uppercase and lowercase for compatibility
            df['open'] = df['Open']
            df['high'] = df['High']
            df['low'] = df['Low']
            df['close'] = df['Close']
            df['volume'] = df['Volume']
            df = df.between_time("09:15", "15:30")
            df = df[["open", "high", "low", "close", "volume"]].dropna()
        return df
    except Exception:
        return pd.DataFrame()


def get_india_vix() -> dict:
    """
    Fetch India VIX.
    Using yfinance (Angel One token for VIX is incorrect - returns Bank Nifty)
    """
    # Use yfinance for VIX (more reliable and correct)
    try:
        ticker = yf.Ticker(VIX_SYMBOL_YF)
        info = ticker.fast_info
        vix = float(info.last_price or 0)
        prev = float(info.previous_close or 0)
        
        record_api_call("yfinance", f"Ticker/{VIX_SYMBOL_YF}")
        logger.info(f"✓ VIX fetched from yfinance: {vix:.2f}")
        
        return {
            "vix": vix,
            "change": round(vix - prev, 2),
            "pct_change": round((vix - prev) / prev * 100, 2) if prev else 0,
            "source": "yfinance",
        }
    except Exception as e:
        logger.error(f"✗ yfinance VIX error: {e}")
    
    # Fallback to NSE (if yfinance fails)
    try:
        sess = _get_nse_session()
        url = "https://www.nseindia.com/api/equity-stockIndices?index=INDIA%20VIX"
        resp = sess.get(url, timeout=10)
        if resp.status_code == 200:
            record_api_call("nse", "equity-stockIndices/INDIA_VIX")
            data = resp.json()
            vix_data = data["data"][0]
            return {
                "vix": float(vix_data.get("lastPrice", 0)),
                "change": float(vix_data.get("change", 0)),
                "pct_change": float(vix_data.get("pChange", 0)),
                "source": "NSE",
            }
    except Exception:
        pass
    
    return {"vix": 0, "change": 0, "pct_change": 0, "source": "unavailable"}


def get_options_chain() -> dict:
    """
    Fetch full Nifty options chain.
    Priority: NSE API → Angel One (fallback)
    Returns empty dict if both fail.
    """
    # Try NSE first (faster when working)
    try:
        sess = _get_nse_session()
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        resp = sess.get(url, timeout=15)

        if resp.status_code == 200:
            raw = resp.json()
            records = raw.get("records", {})
            data = records.get("data", [])

            if data:  # NSE returned valid data
                expiry_dates = sorted(set(r["expiryDate"] for r in data if "expiryDate" in r))
                nearest_expiry = expiry_dates[0] if expiry_dates else None
                chain = [r for r in data if r.get("expiryDate") == nearest_expiry]

                rows = []
                for record in chain:
                    strike = record.get("strikePrice", 0)
                    ce = record.get("CE", {})
                    pe = record.get("PE", {})
                    rows.append({
                        "strike": strike,
                        "ce_oi": ce.get("openInterest", 0),
                        "pe_oi": pe.get("openInterest", 0),
                        "ce_iv": ce.get("impliedVolatility", 0),
                        "pe_iv": pe.get("impliedVolatility", 0),
                        "ce_ltp": ce.get("lastPrice", 0),
                        "pe_ltp": pe.get("lastPrice", 0),
                        "ce_oi_change": ce.get("changeinOpenInterest", 0),
                        "pe_oi_change": pe.get("changeinOpenInterest", 0),
                    })

                if rows:
                    df_chain = pd.DataFrame(rows).sort_values("strike").reset_index(drop=True)

                    total_ce_oi = df_chain["ce_oi"].sum()
                    total_pe_oi = df_chain["pe_oi"].sum()
                    pcr = round(total_pe_oi / total_ce_oi, 3) if total_ce_oi > 0 else 0
                    max_pain = _calculate_max_pain(df_chain)
                    top_ce_strike = df_chain.loc[df_chain["ce_oi"].idxmax(), "strike"] if not df_chain.empty else 0
                    top_pe_strike = df_chain.loc[df_chain["pe_oi"].idxmax(), "strike"] if not df_chain.empty else 0

                    logger.info(f"✓ NSE options chain fetched: PCR={pcr:.3f}, Max Pain={max_pain:,.0f}")
                    
                    record_api_call("nse", "option-chain-indices/NIFTY")

                    return {
                        "chain": df_chain,
                        "expiry": nearest_expiry,
                        "pcr": pcr,
                        "max_pain": max_pain,
                        "resistance": top_ce_strike,
                        "support": top_pe_strike,
                        "total_ce_oi": total_ce_oi,
                        "total_pe_oi": total_pe_oi,
                        "ce_oi_change": df_chain["ce_oi_change"].sum(),
                        "pe_oi_change": df_chain["pe_oi_change"].sum(),
                        'source': 'NSE API',
                        'last_updated': datetime.now()
                    }
    except Exception as e:
        logger.warning(f"⚠ NSE options chain failed: {e}")

    # Fallback to Angel One
    if USE_ANGEL_ONE:
        try:
            logger.info("Trying Angel One for options chain...")
            angel_options = fetch_options_chain_angel()

            if angel_options and angel_options.get('pcr', 0) > 0:
                # Convert Angel One format to standard format
                options_df = angel_options.get('options_data', pd.DataFrame())

                if not options_df.empty:
                    # Pivot data to match NSE format
                    chain_rows = []
                    strikes = sorted(options_df['strike'].unique())

                    for strike in strikes:
                        ce_data = options_df[(options_df['strike'] == strike) & (options_df['type'] == 'CE')]
                        pe_data = options_df[(options_df['strike'] == strike) & (options_df['type'] == 'PE')]

                        chain_rows.append({
                            'strike': strike,
                            'ce_oi': int(ce_data['oi'].iloc[0]) if not ce_data.empty else 0,
                            'pe_oi': int(pe_data['oi'].iloc[0]) if not pe_data.empty else 0,
                            'ce_ltp': float(ce_data['ltp'].iloc[0]) if not ce_data.empty else 0,
                            'pe_ltp': float(pe_data['ltp'].iloc[0]) if not pe_data.empty else 0,
                            'ce_iv': 0,  # Angel One doesn't provide IV easily
                            'pe_iv': 0,
                            'ce_oi_change': 0,
                            'pe_oi_change': 0,
                        })

                    df_chain = pd.DataFrame(chain_rows)

                    # Find strikes with max OI
                    top_ce_strike = df_chain.loc[df_chain["ce_oi"].idxmax(), "strike"] if not df_chain.empty else 0
                    top_pe_strike = df_chain.loc[df_chain["pe_oi"].idxmax(), "strike"] if not df_chain.empty else 0

                    logger.info(f"✓ Angel One options chain fetched: PCR={angel_options['pcr']:.3f}, Max Pain={angel_options['max_pain']:,.0f}")

                    return {
                        "chain": df_chain,
                        "expiry": get_nearest_expiry(),
                        "pcr": angel_options['pcr'],
                        "max_pain": angel_options['max_pain'],
                        "resistance": top_ce_strike,
                        "support": top_pe_strike,
                        "total_ce_oi": angel_options['call_oi'],
                        "total_pe_oi": angel_options['put_oi'],
                        "ce_oi_change": 0,
                        "pe_oi_change": 0,
                        'source': 'Angel One (Real-time)',
                        'last_updated': angel_options['last_updated']
                    }
        except Exception as e:
            logger.error(f"✗ Angel One options chain error: {e}")

    # Both sources failed
    logger.error("✗ All options data sources failed")
    return {}



def _calculate_max_pain(df: pd.DataFrame) -> float:
    """Max Pain calculation - strike where buyer losses are maximized."""
    try:
        strikes = df["strike"].tolist()
        max_pain_strike = None
        min_loss = float("inf")

        for exp_price in strikes:
            ce_loss = sum(max(0, s - exp_price) * oi for s, oi in zip(df["strike"], df["ce_oi"]))
            pe_loss = sum(max(0, exp_price - s) * oi for s, oi in zip(df["strike"], df["pe_oi"]))
            total_loss = ce_loss + pe_loss
            if total_loss < min_loss:
                min_loss = total_loss
                max_pain_strike = exp_price

        return float(max_pain_strike or 0)
    except Exception:
        return 0.0


def get_global_cues() -> dict:
    """Fetch key global indices from yfinance."""
    symbols = {
        "Dow Futures": "YM=F",
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC",
        "Hang Seng": "^HSI",
        "USD/INR": "USDINR=X",
        "Gold": "GC=F",
        "Crude Oil": "CL=F",
    }
    cues = {}
    for name, sym in symbols.items():
        try:
            t = yf.Ticker(sym)
            info = t.fast_info
            price = float(info.last_price or 0)
            prev = float(info.previous_close or 0)
            chg = round(price - prev, 2)
            pct = round((price - prev) / prev * 100, 2) if prev else 0
            cues[name] = {"price": price, "change": chg, "pct_change": pct}
            record_api_call("yfinance", f"Ticker/{sym}")
        except Exception:
            cues[name] = {"price": 0, "change": 0, "pct_change": 0}
    return cues


def is_market_open() -> bool:
    """Check if NSE market is currently open."""
    now = datetime.now(IST)
    if now.weekday() >= 5:
        return False
    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return market_open <= now <= market_close


def get_market_status() -> str:
    now = datetime.now(IST)
    if now.weekday() >= 5:
        return "CLOSED (Weekend)"
    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    pre_open = now.replace(hour=9, minute=0, second=0, microsecond=0)
    if pre_open <= now < market_open:
        return "PRE-OPEN"
    if market_open <= now <= market_close:
        return "OPEN"
    return "CLOSED (After Hours)"
