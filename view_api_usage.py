"""View current API usage with details"""
from api_rate_monitor import load_usage
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

print("="*70)
print("API USAGE SUMMARY")
print("="*70)
print(f"Current Time: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S %Z')}")
print()

# Load usage data
usage = load_usage()

# Display each API
for api_name in ['groq', 'gemini', 'angel_one', 'nse', 'yfinance']:
    api_data = usage.get(api_name, {})
    total = api_data.get('total', 0)
    calls = api_data.get('calls', [])
    
    api_display = api_name.upper().replace('_', ' ')
    print(f"{api_display}:")
    print(f"  Total Calls: {total}")
    
    if calls:
        # Get recent calls
        recent = calls[-3:] if len(calls) > 3 else calls
        print(f"  Recent calls:")
        for call in recent:
            timestamp = call.get('timestamp', 'N/A')
            endpoint = call.get('endpoint', 'N/A')
            print(f"    - {timestamp[:19]} | {endpoint}")
    print()

# Calculate totals
total_ai = usage.get('groq', {}).get('total', 0) + usage.get('gemini', {}).get('total', 0)
total_data = usage.get('angel_one', {}).get('total', 0) + usage.get('nse', {}).get('total', 0) + usage.get('yfinance', {}).get('total', 0)
total_all = total_ai + total_data

print("="*70)
print(f"TOTALS:")
print(f"  AI APIs (Groq + Gemini): {total_ai}")
print(f"  Data APIs (Angel One + NSE + yfinance): {total_data}")
print(f"  Grand Total: {total_all}")
print("="*70)
