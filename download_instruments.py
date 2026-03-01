"""
Download and parse Angel One instrument file for option tokens
"""

import requests
import pandas as pd
import json
from datetime import datetime

print("\n" + "="*70)
print("DOWNLOADING ANGEL ONE INSTRUMENT FILE")
print("="*70 + "\n")

# Download instrument file
print("1. Downloading instrument file (this may take a minute)...")
url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"

try:
    response = requests.get(url, timeout=60)
    if response.status_code == 200:
        instruments = response.json()
        print(f"   [OK] Downloaded {len(instruments)} instruments\n")
    else:
        print(f"   [FAIL] HTTP {response.status_code}\n")
        exit(1)
except Exception as e:
    print(f"   [FAIL] Error: {e}\n")
    exit(1)

# Filter for Nifty options
print("2. Filtering Nifty options...")
nifty_options = [
    i for i in instruments 
    if i.get('name') == 'NIFTY' and i.get('instrumenttype') == 'OPTIDX'
]
print(f"   [OK] Found {len(nifty_options)} Nifty option contracts\n")

# Convert to DataFrame
df = pd.DataFrame(nifty_options)

# Show sample
print("3. Sample data:")
if not df.empty:
    print(df[['symbol', 'token', 'strike', 'expiry', 'instrumenttype']].head(10).to_string(index=False))
    print()

# Get unique expiries
expiries = sorted(df['expiry'].unique())
print(f"4. Available expiries: {len(expiries)}")
for exp in expiries[:5]:
    count = len(df[df['expiry'] == exp])
    print(f"   - {exp}: {count} contracts")
print()

# Save to file
print("5. Saving to instruments_nifty_options.csv...")
df.to_csv('instruments_nifty_options.csv', index=False)
print("   [OK] Saved\n")

# Create token mapping for quick lookup
print("6. Creating token mapping...")
token_map = {}
for _, row in df.iterrows():
    # Angel One stores strikes as float multiplied by 100 (e.g., 2530000.0 for strike 25300)
    strike_value = row['strike']
    # Extract CE/PE from symbol (last 2 characters)
    option_type = row['symbol'][-2:]
    expiry = row['expiry']
    
    # Create key with original strike format
    key = f"{strike_value}_{option_type}_{expiry}"
    token_map[key] = row['token']

# Save token map
with open('token_map.json', 'w') as f:
    json.dump(token_map, f, indent=2)
print(f"   [OK] Created mapping for {len(token_map)} contracts\n")

# Test lookup
print("7. Testing token lookup...")
test_strike = 25300
test_type = "CE"
test_expiry = "02MAR2026"  # Use known expiry

# Angel One format: strike * 100
strike_formatted = float(test_strike * 100)
key = f"{strike_formatted}_{test_type}_{test_expiry}"
token = token_map.get(key)

print(f"   Strike: {test_strike} {test_type}")
print(f"   Expiry: {test_expiry}")
print(f"   Key: {key}")
print(f"   Token: {token}")
print()

print("="*70)
print("DOWNLOAD COMPLETE")
print("="*70 + "\n")

print("Files created:")
print("  - instruments_nifty_options.csv (full data)")
print("  - token_map.json (quick lookup)")
print("\nNext: Update angel_one_fetcher.py to use token_map.json\n")
