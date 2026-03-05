"""Test NSE options chain directly"""
import requests
from data_fetcher import _get_nse_session, NSE_HEADERS
import json

print("="*70)
print("TESTING NSE OPTIONS CHAIN")
print("="*70)

try:
    # Get NSE session
    sess = _get_nse_session()
    print("\n✓ NSE session created")
    
    # Try to fetch options chain
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    print(f"\nFetching: {url}")
    
    resp = sess.get(url, timeout=15)
    print(f"Status Code: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"\nResponse keys: {list(data.keys())}")
        records = data.get("records", {})
        print(f"Records keys: {list(records.keys()) if records else 'None'}")
        option_data = records.get("data", [])
        
        print(f"\n✓ Got {len(option_data)} option records")
        
        # Debug: print first record if available
        if option_data:
            print(f"\nFirst record sample:")
            print(json.dumps(option_data[0], indent=2)[:500])
        
        if option_data:
            # Get expiry dates
            expiry_dates = sorted(set(r["expiryDate"] for r in option_data if "expiryDate" in r))
            print(f"Expiry dates: {expiry_dates[:3]}")
            
            # Filter for nearest expiry
            nearest_expiry = expiry_dates[0]
            chain = [r for r in option_data if r.get("expiryDate") == nearest_expiry]
            print(f"Records for {nearest_expiry}: {len(chain)}")
            
            # Calculate PCR
            total_ce_oi = sum(r.get("CE", {}).get("openInterest", 0) for r in chain)
            total_pe_oi = sum(r.get("PE", {}).get("openInterest", 0) for r in chain)
            pcr = total_pe_oi / total_ce_oi if total_ce_oi > 0 else 0
            
            print(f"\n✓ PCR: {pcr:.3f}")
            print(f"  Call OI: {total_ce_oi:,}")
            print(f"  Put OI: {total_pe_oi:,}")
        else:
            print("\n✗ No option data in response")
    else:
        print(f"\n✗ Failed with status {resp.status_code}")
        print(f"Response: {resp.text[:200]}")
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("="*70)
