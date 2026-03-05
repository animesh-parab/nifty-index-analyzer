"""Test options chain and PCR fetching"""
from data_fetcher import get_options_chain
import json

print("="*70)
print("TESTING OPTIONS CHAIN & PCR")
print("="*70)

# Fetch options chain
oi_data = get_options_chain()

print("\nOptions Chain Data:")
print(json.dumps(oi_data, indent=2, default=str))

print("\n" + "="*70)
print("KEY VALUES:")
print(f"PCR: {oi_data.get('pcr', 'N/A')}")
print(f"Max Pain: {oi_data.get('max_pain', 'N/A')}")
print(f"Call OI: {oi_data.get('call_oi', 'N/A')}")
print(f"Put OI: {oi_data.get('put_oi', 'N/A')}")
print(f"Source: {oi_data.get('source', 'N/A')}")
print(f"Last Updated: {oi_data.get('last_updated', 'N/A')}")
print("="*70)
