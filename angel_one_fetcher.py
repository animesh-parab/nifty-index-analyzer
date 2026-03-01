"""
angel_one_fetcher.py
Angel One SmartAPI Data Fetcher - Real-time market data

Provides real-time Nifty data, VIX, options chain, and historical candles
using Angel One SmartAPI (100% FREE)
"""

import os
import pandas as pd
import time
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from SmartApi import SmartConnect
import pyotp

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Angel One credentials
API_KEY = os.getenv('ANGEL_API_KEY')
CLIENT_ID = os.getenv('ANGEL_CLIENT_ID')
MPIN = os.getenv('ANGEL_MPIN')
TOTP_SECRET = os.getenv('ANGEL_TOTP_SECRET')
FEED_TOKEN = os.getenv('ANGEL_FEED_TOKEN')
REFRESH_TOKEN = os.getenv('ANGEL_REFRESH_TOKEN')

# Symbol tokens for Angel One
NIFTY_TOKEN = "99926000"  # NIFTY 50 index
INDIA_VIX_TOKEN = "99926009"  # India VIX

# Global SmartAPI instance
_smart_api = None


def get_smart_api():
    """Get or create SmartAPI instance with authentication"""
    global _smart_api
    
    if _smart_api is None:
        try:
            _smart_api = SmartConnect(api_key=API_KEY)
            
            # Generate new session with TOTP
            totp = pyotp.TOTP(TOTP_SECRET).now()
            data = _smart_api.generateSession(CLIENT_ID, MPIN, totp)
            
            if data['status']:
                print("✓ Angel One login successful")
                # Tokens are automatically set by generateSession
            else:
                print(f"✗ Angel One login failed: {data.get('message')}")
                return None
                    
        except Exception as e:
            print(f"✗ Angel One connection error: {e}")
            return None
    
    return _smart_api


def fetch_nifty_angel(index="NIFTY") -> dict:
    """
    Fetch real-time Nifty 50 or Bank Nifty price from Angel One
    
    Args:
        index: "NIFTY" or "BANKNIFTY"
    
    Returns:
        dict: {
            'price': float,
            'change': float,
            'change_percent': float,
            'open': float,
            'high': float,
            'low': float,
            'close': float,
            'timestamp': datetime,
            'source': 'Angel One'
        }
    """
    try:
        smart_api = get_smart_api()
        if not smart_api:
            return None
        
        # Select symbol and token based on index
        if index == "NIFTY":
            symbol = "NIFTY 50"
            token = NIFTY_TOKEN
        else:  # BANKNIFTY
            symbol = "NIFTY BANK"
            token = "99926009"  # Bank Nifty token
        
        # Get LTP (Last Traded Price) data
        response = smart_api.ltpData("NSE", symbol, token)
        
        if response and response.get('status'):
            data = response['data']
            ltp = float(data['ltp'])
            open_price = float(data.get('open', ltp))
            high = float(data.get('high', ltp))
            low = float(data.get('low', ltp))
            close = float(data.get('close', ltp))
            
            change = ltp - close
            change_percent = (change / close) * 100 if close > 0 else 0
            
            return {
                'price': ltp,
                'change': change,
                'change_percent': change_percent,
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'timestamp': datetime.now(),
                'source': 'Angel One (Real-time)'
            }
        else:
            print(f"✗ Angel One LTP error: {response.get('message')}")
            return None
            
    except Exception as e:
        print(f"✗ Angel One fetch error: {e}")
        return None


def fetch_vix_angel() -> dict:
    """
    Fetch real-time India VIX from Angel One
    
    Returns:
        dict: {
            'vix': float,
            'change': float,
            'change_percent': float,
            'timestamp': datetime,
            'source': 'Angel One'
        }
    """
    try:
        smart_api = get_smart_api()
        if not smart_api:
            return None
        
        # Get VIX data
        response = smart_api.ltpData("NSE", "INDIA VIX", INDIA_VIX_TOKEN)
        
        if response and response.get('status'):
            data = response['data']
            vix = float(data['ltp'])
            close = float(data.get('close', vix))
            
            change = vix - close
            change_percent = (change / close) * 100 if close > 0 else 0
            
            return {
                'vix': vix,
                'change': change,
                'change_percent': change_percent,
                'timestamp': datetime.now(),
                'source': 'Angel One (Real-time)'
            }
        else:
            print(f"✗ Angel One VIX error: {response.get('message')}")
            return None
            
    except Exception as e:
        print(f"✗ Angel One VIX fetch error: {e}")
        return None


def fetch_candles_angel(index="NIFTY", interval: str = "FIVE_MINUTE", days: int = 5) -> pd.DataFrame:
    """
    Fetch historical candle data from Angel One
    
    Args:
        index: "NIFTY" or "BANKNIFTY"
        interval: Candle interval (ONE_MINUTE, FIVE_MINUTE, FIFTEEN_MINUTE, etc.)
        days: Number of days of historical data
    
    Returns:
        DataFrame with columns: timestamp, open, high, low, close, volume
    """
    try:
        smart_api = get_smart_api()
        if not smart_api:
            return pd.DataFrame()
        
        # Select symbol and token based on index
        if index == "NIFTY":
            symbol = "NIFTY 50"
            token = NIFTY_TOKEN
        else:  # BANKNIFTY
            symbol = "NIFTY BANK"
            token = "99926009"  # Bank Nifty token
        
        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days)
        
        # Format dates for Angel One API
        from_date_str = from_date.strftime("%Y-%m-%d %H:%M")
        to_date_str = to_date.strftime("%Y-%m-%d %H:%M")
        
        # Get historical data
        response = smart_api.getCandleData({
            "exchange": "NSE",
            "symboltoken": token,
            "interval": interval,
            "fromdate": from_date_str,
            "todate": to_date_str
        })
        
        if response and response.get('status'):
            candles = response['data']
            
            # Convert to DataFrame
            df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Convert price columns to float
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            return df
        else:
            print(f"✗ Angel One candles error: {response.get('message')}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"✗ Angel One candles fetch error: {e}")
        return pd.DataFrame()


def fetch_options_chain_angel(expiry_date: str = None) -> dict:
    """
    Fetch options chain data from Angel One
    
    Args:
        expiry_date: Expiry date in format 'DDMMMYYYY' (e.g., '27FEB2026')
                    If None, uses nearest expiry
    
    Returns:
        dict: {
            'pcr': float,  # Put-Call Ratio
            'max_pain': float,
            'call_oi': int,
            'put_oi': int,
            'options_data': DataFrame,
            'last_updated': datetime
        }
    """
    try:
        smart_api = get_smart_api()
        if not smart_api:
            return None
        
        # Get current Nifty price to determine ATM strike
        nifty_data = fetch_nifty_angel()
        if not nifty_data:
            return None
        
        current_price = nifty_data['price']
        atm_strike = round(current_price / 50) * 50  # Round to nearest 50
        
        # Get nearest expiry if not provided
        if not expiry_date:
            expiry_date = get_nearest_expiry()
        
        # Get options data for strikes around ATM (±10 strikes = 21 total)
        strikes = [atm_strike + (i * 50) for i in range(-10, 11)]
        
        options_data = []
        total_call_oi = 0
        total_put_oi = 0
        
        print(f"Fetching options chain for {len(strikes)} strikes around ATM {atm_strike}...")
        
        # Fetch each strike (CE and PE)
        for idx, strike in enumerate(strikes):
            try:
                # Fetch Call Option (CE)
                ce_symbol = f"NIFTY{expiry_date}{strike}CE"
                ce_token = get_option_token(strike, 'CE', expiry_date)
                
                # Use quote API instead of ltpData to get OI
                ce_response = smart_api.getMarketData("FULL", [{"exchange": "NFO", "tradingsymbol": ce_symbol, "symboltoken": ce_token}]) if ce_token else None
                
                if ce_response and ce_response.get('status'):
                    ce_data = ce_response['data']['fetched'][0] if ce_response['data'].get('fetched') else {}
                    ce_oi = int(ce_data.get('oi', 0))
                    total_call_oi += ce_oi
                    
                    options_data.append({
                        'strike': strike,
                        'type': 'CE',
                        'ltp': float(ce_data.get('ltp', 0)),
                        'oi': ce_oi,
                        'volume': int(ce_data.get('volume', 0))
                    })
                
                # Fetch Put Option (PE)
                pe_symbol = f"NIFTY{expiry_date}{strike}PE"
                pe_token = get_option_token(strike, 'PE', expiry_date)
                
                pe_response = smart_api.getMarketData("FULL", [{"exchange": "NFO", "tradingsymbol": pe_symbol, "symboltoken": pe_token}]) if pe_token else None
                
                if pe_response and pe_response.get('status'):
                    pe_data = pe_response['data']['fetched'][0] if pe_response['data'].get('fetched') else {}
                    pe_oi = int(pe_data.get('oi', 0))
                    total_put_oi += pe_oi
                    
                    options_data.append({
                        'strike': strike,
                        'type': 'PE',
                        'ltp': float(pe_data.get('ltp', 0)),
                        'oi': pe_oi,
                        'volume': int(pe_data.get('volume', 0))
                    })
                
                # Rate limiting: 0.1 second delay (10 calls/second limit)
                time.sleep(0.1)
                
                # Progress indicator
                if (idx + 1) % 5 == 0:
                    print(f"  Progress: {idx + 1}/{len(strikes)} strikes fetched...")
                    
            except Exception as e:
                print(f"  ⚠ Error fetching strike {strike}: {e}")
                continue
        
        # Calculate PCR (Put-Call Ratio)
        pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 0
        
        # Calculate Max Pain
        max_pain = calculate_max_pain_from_data(options_data, strikes)
        
        print(f"✓ Options chain fetched: PCR={pcr:.3f}, Max Pain={max_pain}, Total OI={total_call_oi + total_put_oi:,}")
        
        return {
            'pcr': pcr,
            'max_pain': max_pain,
            'call_oi': total_call_oi,
            'put_oi': total_put_oi,
            'options_data': pd.DataFrame(options_data),
            'last_updated': datetime.now(),
            'source': 'Angel One (Real-time)'
        }
        
    except Exception as e:
        print(f"✗ Angel One options chain error: {e}")
        return None


def get_nearest_expiry() -> str:
    """
    Get nearest available expiry date from instrument file
    Returns: 'DDMMMYYYY' (e.g., '02MAR2026')
    """
    try:
        import pandas as pd
        import os
        from datetime import datetime
        
        # Load instrument file
        instruments_file = 'instruments_nifty_options.csv'
        
        if not os.path.exists(instruments_file):
            logger.warning(f"⚠ Instrument file not found. Run: python download_instruments.py")
            # Fallback to calculation
            return _calculate_next_thursday()
        
        # Read expiries from file
        df = pd.read_csv(instruments_file)
        expiries = sorted(df['expiry'].unique())
        
        # Get today's date
        today = datetime.now()
        
        # Find nearest future expiry
        for expiry_str in expiries:
            try:
                expiry_date = datetime.strptime(expiry_str, '%d%b%Y')
                if expiry_date >= today:
                    logger.info(f"✓ Using expiry: {expiry_str}")
                    return expiry_str
            except:
                continue
        
        # If no future expiry found, use first one
        if expiries:
            return expiries[0]
        
        # Fallback
        return _calculate_next_thursday()
        
    except Exception as e:
        logger.error(f"✗ Error getting expiry: {e}")
        return _calculate_next_thursday()


def _calculate_next_thursday() -> str:
    """
    Calculate next Thursday expiry date (fallback method)
    Returns: 'DDMMMYYYY' (e.g., '05MAR2026')
    """
    from datetime import datetime, timedelta
    
    today = datetime.now()
    
    # Find next Thursday
    days_ahead = 3 - today.weekday()  # Thursday is 3
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    
    next_thursday = today + timedelta(days=days_ahead)
    
    # Format as DDMMMYYYY
    return next_thursday.strftime('%d%b%Y').upper()


def get_option_token(strike: int, option_type: str, expiry: str) -> str:
    """
    Get Angel One token for option contract using local instrument file
    
    Args:
        strike: Strike price (e.g., 25300)
        option_type: 'CE' or 'PE'
        expiry: Expiry date in format 'DDMMMYYYY' (e.g., '05MAR2026')
    
    Returns:
        str: Symbol token or None if not found
    """
    try:
        import json
        import os
        
        # Load token map (created by download_instruments.py)
        token_map_file = 'token_map.json'
        
        if not os.path.exists(token_map_file):
            logger.warning(f"⚠ Token map file not found. Run: python download_instruments.py")
            return None
        
        with open(token_map_file, 'r') as f:
            token_map = json.load(f)
        
        # Angel One stores strikes multiplied by 100 with .000000
        # e.g., 25300 becomes "2530000.000000"
        strike_formatted = strike * 100
        
        # Try different key formats
        keys_to_try = [
            f"{float(strike_formatted)}_{ option_type}_{expiry}",  # 2530000.0_CE_05MAR2026
            f"{strike_formatted}.000000_{option_type}_{expiry}",  # 2530000.000000_CE_05MAR2026
            f"{int(strike_formatted)}_{option_type}_{expiry}",  # 2530000_CE_05MAR2026
        ]
        
        for key in keys_to_try:
            if key in token_map:
                token = token_map[key]
                return str(token)
        
        logger.warning(f"⚠ Token not found for strike {strike} {option_type} expiry {expiry}")
        return None
            
    except Exception as e:
        logger.error(f"✗ Error getting token: {e}")
        return None


def calculate_max_pain_from_data(options_data: list, strikes: list) -> float:
    """
    Calculate Max Pain strike from options data
    
    Max Pain = Strike where option sellers (writers) lose least money
    """
    if not options_data or not strikes:
        return 0
    
    # Group data by strike
    strike_data = {}
    for option in options_data:
        strike = option['strike']
        if strike not in strike_data:
            strike_data[strike] = {'ce_oi': 0, 'pe_oi': 0}
        
        if option['type'] == 'CE':
            strike_data[strike]['ce_oi'] = option['oi']
        else:
            strike_data[strike]['pe_oi'] = option['oi']
    
    # Calculate pain for each strike
    pain_values = {}
    for test_strike in strikes:
        total_pain = 0
        
        for strike, data in strike_data.items():
            # Call writers lose money if price > strike
            if test_strike > strike:
                total_pain += (test_strike - strike) * data['ce_oi']
            
            # Put writers lose money if price < strike
            if test_strike < strike:
                total_pain += (strike - test_strike) * data['pe_oi']
        
        pain_values[test_strike] = total_pain
    
    # Max Pain = strike with minimum total pain
    if pain_values:
        max_pain_strike = min(pain_values, key=pain_values.get)
        return max_pain_strike
    
    return 0


# Test function
if __name__ == "__main__":
    print("\n" + "="*70)
    print("TESTING ANGEL ONE DATA FETCHER")
    print("="*70 + "\n")
    
    # Test Nifty price
    print("1. Testing Nifty 50 price...")
    nifty = fetch_nifty_angel()
    if nifty:
        print(f"   ✓ Nifty: {nifty['price']:.2f} ({nifty['change']:+.2f}, {nifty['change_percent']:+.2f}%)")
        print(f"   Source: {nifty['source']}")
    else:
        print("   ✗ Failed to fetch Nifty data")
    
    # Test VIX
    print("\n2. Testing India VIX...")
    vix = fetch_vix_angel()
    if vix:
        print(f"   ✓ VIX: {vix['vix']:.2f} ({vix['change']:+.2f}, {vix['change_percent']:+.2f}%)")
        print(f"   Source: {vix['source']}")
    else:
        print("   ✗ Failed to fetch VIX data")
    
    # Test candles
    print("\n3. Testing candle data...")
    candles = fetch_candles_angel(interval="FIVE_MINUTE", days=1)
    if not candles.empty:
        print(f"   ✓ Fetched {len(candles)} candles")
        print(f"   Latest: {candles.iloc[-1]['close']:.2f} at {candles.iloc[-1]['timestamp']}")
    else:
        print("   ✗ Failed to fetch candle data")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70 + "\n")
