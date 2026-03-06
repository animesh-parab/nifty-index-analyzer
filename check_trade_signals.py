"""
Quick script to check if any trade signals have formed
"""

from trade_signal_scanner import scan_for_signals
from data_fetcher import get_candle_data
from indicators import calculate_all_indicators
import json
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

print("="*70)
print("TRADE SIGNAL SCANNER - CURRENT STATUS")
print("="*70)
print(f"Time: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}")
print("="*70)

# Fetch and prepare data
print("\nFetching candle data...")
df = get_candle_data('NIFTY')

if df.empty:
    print("❌ ERROR: Could not fetch candle data")
    exit(1)

print(f"✓ Fetched {len(df)} candles")

# Calculate indicators
print("Calculating indicators...")
df = calculate_all_indicators(df)

# Get current price
current_price = df.iloc[-1]['close']
print(f"✓ Current Nifty Price: {current_price:.2f}")

# Prepare data for scanner (needs lowercase columns)
df_for_scanner = df.copy()
df_for_scanner.columns = [col.lower() for col in df_for_scanner.columns]

# Scan for signals
print("\nScanning for trade signals...")
signal = scan_for_signals(df_for_scanner)

print("\n" + "="*70)
print("SIGNAL RESULT")
print("="*70)

signal_type = signal.get('signal', 'NO_TRADE')

if signal_type == 'BUY':
    print("🟢 CALL SETUP DETECTED!")
    print("="*70)
    print(f"Setup Type: {signal.get('setup_type', 'N/A')}")
    print(f"Entry: ₹{signal.get('entry', 0):,.2f}")
    print(f"Stop Loss: ₹{signal.get('stop_loss', 0):,.2f}")
    print(f"Target 1: ₹{signal.get('target_1', 0):,.2f}")
    print(f"Target 2: ₹{signal.get('target_2', 0):,.2f}")
    print(f"Risk: {signal.get('risk', 0):.2f} points")
    print(f"Reward: {signal.get('reward', 0):.2f} points")
    print(f"Risk:Reward: 1:{signal.get('risk_reward_ratio', 0):.2f}")
    print(f"Confluence: {signal.get('confluence_score', 0)}/{signal.get('total_conditions', 7)}")
    print(f"Confidence: {signal.get('confidence', 0)}%")
    print(f"Position in Range: {signal.get('position_in_range', 0):.1%}")
    print(f"RSI: {signal.get('rsi', 0):.1f} (Rising: {signal.get('rsi_rising', False)})")
    print(f"Candles Since Low: {signal.get('candles_since_low', 0)}")
    print(f"Time: {signal.get('time', 'N/A')}")
    
elif signal_type == 'SELL':
    print("🔴 PUT SETUP DETECTED!")
    print("="*70)
    print(f"Setup Type: {signal.get('setup_type', 'N/A')}")
    print(f"Entry: ₹{signal.get('entry', 0):,.2f}")
    print(f"Stop Loss: ₹{signal.get('stop_loss', 0):,.2f}")
    print(f"Target 1: ₹{signal.get('target_1', 0):,.2f}")
    print(f"Target 2: ₹{signal.get('target_2', 0):,.2f}")
    print(f"Risk: {signal.get('risk', 0):.2f} points")
    print(f"Reward: {signal.get('reward', 0):.2f} points")
    print(f"Risk:Reward: 1:{signal.get('risk_reward_ratio', 0):.2f}")
    print(f"Confluence: {signal.get('confluence_score', 0)}/{signal.get('total_conditions', 7)}")
    print(f"Confidence: {signal.get('confidence', 0)}%")
    print(f"Position in Range: {signal.get('position_in_range', 0):.1%}")
    print(f"RSI: {signal.get('rsi', 0):.1f}")
    print(f"Rally Size: {signal.get('rally_size', 0):.2f} points")
    print(f"Time: {signal.get('time', 'N/A')}")
    
else:
    print("⚪ NO TRADE SIGNAL")
    print("="*70)
    print(f"Reason: {signal.get('reason', 'N/A')}")

print("\n" + "="*70)
print("DETAILED SIGNAL DATA")
print("="*70)
print(json.dumps(signal, indent=2, default=str))
print("="*70)
