"""Quick test of token lookup and options fetch"""

print("\nTesting Angel One Options Implementation\n")
print("="*60)

# Test 1: Token lookup
print("\n1. Testing token lookup...")
from angel_one_fetcher import get_option_token

expiry = "02MAR2026"
strike = 25300

ce_token = get_option_token(strike, 'CE', expiry)
pe_token = get_option_token(strike, 'PE', expiry)

print(f"   Strike {strike} CE: {ce_token}")
print(f"   Strike {strike} PE: {pe_token}")

if ce_token and pe_token:
    print("   [SUCCESS] Token lookup working!")
else:
    print("   [FAILED] Token lookup not working")
    exit(1)

# Test 2: Full options chain
print("\n2. Testing full options chain fetch...")
print("   (This takes ~10 seconds)")

from angel_one_fetcher import fetch_options_chain_angel

options = fetch_options_chain_angel()

if options and options.get('pcr', 0) > 0:
    print(f"\n   [SUCCESS] Options chain fetched!")
    print(f"   PCR: {options['pcr']:.3f}")
    print(f"   Max Pain: {options['max_pain']:,.0f}")
    print(f"   Total Call OI: {options['call_oi']:,}")
    print(f"   Total Put OI: {options['put_oi']:,}")
    print(f"   Total OI: {options['call_oi'] + options['put_oi']:,}")
else:
    print("\n   [FAILED] Options chain returned no data")
    print(f"   PCR: {options.get('pcr', 0) if options else 0}")

print("\n" + "="*60)
print("Test complete!\n")
