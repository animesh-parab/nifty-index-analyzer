"""
angel_one_setup.py
Angel One SmartAPI Setup and Testing

IMPORTANT: You need to register at https://smartapi.angelbroking.com/
and get your API credentials before using this.
"""

import sys
import os
from dotenv import load_dotenv

print("\n" + "="*70)
print("ANGEL ONE SMARTAPI SETUP")
print("="*70 + "\n")

# Step 1: Check if smartapi is installed
print("Step 1: Checking SmartAPI installation...")
try:
    from SmartApi import SmartConnect
    import pyotp
    print("   ✓ SmartAPI Python library is installed\n")
except ImportError:
    print("   ✗ SmartAPI not installed")
    print("\n   Installing now...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "smartapi-python", "logzero", "pyotp"])
    print("   ✓ SmartAPI installed successfully\n")
    from SmartApi import SmartConnect
    import pyotp

# Step 2: Load credentials from .env
print("Step 2: Loading credentials from .env file...")
load_dotenv()

api_key = os.getenv('ANGEL_API_KEY')
client_id = os.getenv('ANGEL_CLIENT_ID')
mpin = os.getenv('ANGEL_MPIN')  # Changed from password to MPIN
totp_secret = os.getenv('ANGEL_TOTP_SECRET')

if not all([api_key, client_id, mpin]):
    print("   ✗ Missing credentials in .env file")
    print("\n   Please add the following to your .env file:")
    print("   ANGEL_API_KEY=your_api_key")
    print("   ANGEL_CLIENT_ID=your_client_id")
    print("   ANGEL_MPIN=your_4_digit_mpin")
    print("   ANGEL_TOTP_SECRET=your_totp_secret")
    sys.exit(1)

print(f"   ✓ API Key: {api_key[:4]}...{api_key[-4:]}")
print(f"   ✓ Client ID: {client_id}")
print(f"   ✓ MPIN: {'*' * len(mpin)}")
if totp_secret:
    print(f"   ✓ TOTP Secret: {totp_secret[:4]}...{totp_secret[-4:]}\n")
else:
    print("   ⚠ TOTP Secret not found (will prompt for code)\n")

# Step 3: Test connection
print("\n" + "="*70)
print("TESTING CONNECTION")
print("="*70 + "\n")

try:
    # Initialize SmartConnect
    smart_api = SmartConnect(api_key=api_key)
    print("✓ SmartConnect initialized")
    
    # Generate TOTP
    if totp_secret:
        totp = pyotp.TOTP(totp_secret).now()
        print(f"✓ Generated TOTP: {totp}")
    else:
        totp = input("Enter TOTP from your authenticator app: ").strip()
    
    # Login
    print("✓ Attempting login...")
    data = smart_api.generateSession(client_id, mpin, totp)
    
    if data['status']:
        print("\n✓ LOGIN SUCCESSFUL!")
        print(f"\nYour details:")
        print(f"  Client ID: {data['data']['clientcode']}")
        print(f"  Name: {data['data']['name']}")
        print(f"  Feed Token: {data['data']['feedToken'][:20]}...")
        print(f"  Refresh Token: {data['data']['refreshToken'][:20]}...")
        
        # Update .env file with tokens
        print("\n" + "="*70)
        print("SAVING TOKENS TO .ENV")
        print("="*70 + "\n")
        
        # Read existing .env content
        with open('.env', 'r') as f:
            env_content = f.read()
        
        # Remove old token lines if they exist
        lines = env_content.split('\n')
        new_lines = [line for line in lines if not line.startswith('ANGEL_FEED_TOKEN=') and not line.startswith('ANGEL_REFRESH_TOKEN=')]
        
        # Add new tokens
        new_lines.append(f"ANGEL_FEED_TOKEN={data['data']['feedToken']}")
        new_lines.append(f"ANGEL_REFRESH_TOKEN={data['data']['refreshToken']}")
        
        # Write back to .env
        with open('.env', 'w') as f:
            f.write('\n'.join(new_lines))
        
        print("✓ Tokens saved to .env file")
        print("\nYou can now use Angel One SmartAPI in your application!")
        print("\n⚠ Note: Tokens expire after 24 hours. Re-run this script to refresh.")
        
    else:
        print("\n✗ LOGIN FAILED")
        print(f"Error: {data.get('message', 'Unknown error')}")
        print(f"Full response: {data}")
        
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    print("\nCommon issues:")
    print("  1. Invalid credentials")
    print("  2. Wrong TOTP code")
    print("  3. Account not activated for API trading")
    print("  4. Network issues")
    print("\nPlease check and try again")

print("\n" + "="*70)
print("SETUP COMPLETE")
print("="*70 + "\n")
