"""
Robust NSE Options Chain Fetcher
Uses better session management and retry logic
"""

import requests
import time
import random
from datetime import datetime

# NSE headers to mimic browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.nseindia.com/option-chain",
    "Connection": "keep-alive",
    "DNT": "1",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


def create_nse_session():
    """Create NSE session with proper cookies"""
    session = requests.Session()
    session.headers.update(HEADERS)
    
    # Visit homepage first to get cookies
    try:
        homepage = session.get("https://www.nseindia.com", timeout=10)
        print(f"Homepage status: {homepage.status_code}")
        time.sleep(random.uniform(1, 2))  # Random delay
        return session
    except Exception as e:
        print(f"Error creating session: {e}")
        return None


def fetch_nse_options_chain(max_retries=3):
    """Fetch NSE options chain with retry logic"""
    
    for attempt in range(max_retries):
        try:
            print(f"\nAttempt {attempt + 1}/{max_retries}")
            
            # Create fresh session
            session = create_nse_session()
            if not session:
                continue
            
            # Fetch options chain
            url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
            print(f"Fetching: {url}")
            
            response = session.get(url, timeout=15)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if we got data
                if not data or not isinstance(data, dict):
                    print("Empty or invalid response")
                    continue
                
                records = data.get("records", {})
                if not records:
                    print("No records in response")
                    continue
                
                option_data = records.get("data", [])
                if not option_data:
                    print("No option data in records")
                    continue
                
                # Success!
                print(f"✓ Got {len(option_data)} option records")
                
                # Calculate PCR
                expiry_dates = sorted(set(r["expiryDate"] for r in option_data if "expiryDate" in r))
                nearest_expiry = expiry_dates[0] if expiry_dates else None
                chain = [r for r in option_data if r.get("expiryDate") == nearest_expiry]
                
                total_ce_oi = sum(r.get("CE", {}).get("openInterest", 0) for r in chain)
                total_pe_oi = sum(r.get("PE", {}).get("openInterest", 0) for r in chain)
                pcr = total_pe_oi / total_ce_oi if total_ce_oi > 0 else 0
                
                print(f"\n✓ SUCCESS!")
                print(f"  Expiry: {nearest_expiry}")
                print(f"  PCR: {pcr:.3f}")
                print(f"  Call OI: {total_ce_oi:,}")
                print(f"  Put OI: {total_pe_oi:,}")
                
                return {
                    'pcr': pcr,
                    'call_oi': total_ce_oi,
                    'put_oi': total_pe_oi,
                    'expiry': nearest_expiry,
                    'source': 'NSE API',
                    'timestamp': datetime.now()
                }
                
            elif response.status_code == 401:
                print("Unauthorized - session expired")
            elif response.status_code == 403:
                print("Forbidden - might be blocked")
            else:
                print(f"Unexpected status: {response.status_code}")
            
        except requests.exceptions.Timeout:
            print(f"Timeout on attempt {attempt + 1}")
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {e}")
        
        # Wait before retry
        if attempt < max_retries - 1:
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            print(f"Waiting {wait_time:.1f}s before retry...")
            time.sleep(wait_time)
    
    print("\n✗ All attempts failed")
    return None


if __name__ == "__main__":
    print("="*70)
    print("ROBUST NSE OPTIONS CHAIN TEST")
    print("="*70)
    
    result = fetch_nse_options_chain()
    
    if result:
        print("\n" + "="*70)
        print("FINAL RESULT:")
        print(f"PCR: {result['pcr']:.3f}")
        print(f"Call OI: {result['call_oi']:,}")
        print(f"Put OI: {result['put_oi']:,}")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("FAILED TO GET OPTIONS DATA")
        print("="*70)
