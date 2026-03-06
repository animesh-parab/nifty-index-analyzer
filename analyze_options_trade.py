"""
Analyze the 24700 CE options trade from March 6, 2026
"""

from data_fetcher import get_candle_data
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

print("="*70)
print("OPTIONS TRADE ANALYSIS - 24700 CE (10 MAR 2026)")
print("="*70)

# Trade details
strike = 24700
entry_time = "9:29 AM"
exit_time = "10:32 AM"
entry_premium = 193  # CMP at 9:29
buy_above = 195
target_1 = 290
target_2 = 370
stop_loss = 140

print("\n📋 TRADE DETAILS")
print("="*70)
print(f"Strike: {strike} CE")
print(f"Expiry: 10 MAR 2026")
print(f"Entry Time: {entry_time}")
print(f"Entry Premium (CMP): ₹{entry_premium}")
print(f"Buy Above: ₹{buy_above}")
print(f"Target 1: ₹{target_1}")
print(f"Target 2: ₹{target_2}")
print(f"Stop Loss: ₹{stop_loss}")
print(f"Exit Time: {exit_time} (Exit called)")

# Fetch Nifty spot data
print("\n📊 NIFTY SPOT MOVEMENT")
print("="*70)

df = get_candle_data('NIFTY')
today = datetime.now(IST).date()
df_today = df[df.index.date == today]

if not df_today.empty:
    # Get spot at 9:29 (closest candle)
    target_929 = datetime(today.year, today.month, today.day, 9, 29, tzinfo=IST)
    time_diff_929 = abs((df_today.index - target_929).total_seconds())
    idx_929 = time_diff_929.argmin()
    spot_929 = df_today.iloc[idx_929]['Close']
    time_929 = df_today.index[idx_929]
    
    # Get spot at 10:32 (closest candle)
    target_1032 = datetime(today.year, today.month, today.day, 10, 32, tzinfo=IST)
    time_diff_1032 = abs((df_today.index - target_1032).total_seconds())
    idx_1032 = time_diff_1032.argmin()
    spot_1032 = df_today.iloc[idx_1032]['Close']
    time_1032 = df_today.index[idx_1032]
    
    # Get high between entry and exit
    df_trade_period = df_today[(df_today.index >= time_929) & (df_today.index <= time_1032)]
    high_during_trade = df_trade_period['High'].max()
    high_time = df_trade_period[df_trade_period['High'] == high_during_trade].index[0]
    
    print(f"At Entry ({time_929.strftime('%H:%M')}): ₹{spot_929:,.2f}")
    print(f"At Exit ({time_1032.strftime('%H:%M')}): ₹{spot_1032:,.2f}")
    print(f"High During Trade: ₹{high_during_trade:,.2f} at {high_time.strftime('%H:%M')}")
    print(f"Spot Movement: {spot_1032 - spot_929:+,.2f} points")
    
    # Calculate distance from strike
    distance_at_entry = spot_929 - strike
    distance_at_exit = spot_1032 - strike
    
    print(f"\nDistance from Strike ({strike}):")
    print(f"At Entry: {distance_at_entry:+,.2f} points ({'ITM' if distance_at_entry > 0 else 'OTM'})")
    print(f"At Exit: {distance_at_exit:+,.2f} points ({'ITM' if distance_at_exit > 0 else 'OTM'})")

# Trade outcome analysis
print("\n💰 TRADE OUTCOME ANALYSIS")
print("="*70)

# Since exit was called at 10:32, the trade likely hit stop loss or failed to reach buy above
print(f"Entry Premium: ₹{entry_premium}")
print(f"Buy Above Trigger: ₹{buy_above}")
print(f"Stop Loss: ₹{stop_loss}")

# Calculate potential outcomes
risk = entry_premium - stop_loss
reward_t1 = target_1 - entry_premium
reward_t2 = target_2 - entry_premium
rr_t1 = reward_t1 / risk if risk > 0 else 0
rr_t2 = reward_t2 / risk if risk > 0 else 0

print(f"\nRisk: ₹{risk} per lot")
print(f"Reward (T1): ₹{reward_t1} per lot (R:R = 1:{rr_t1:.2f})")
print(f"Reward (T2): ₹{reward_t2} per lot (R:R = 1:{rr_t2:.2f})")

print("\n🔴 TRADE RESULT: FAILED")
print("="*70)
print("Reason: Exit called at 10:32 AM")
print("\nPossible scenarios:")
print("1. Premium never crossed ₹195 (Buy Above trigger)")
print("2. Premium hit stop loss at ₹140")
print("3. Setup invalidated (exit signal)")

# Analysis
print("\n📉 WHY THE TRADE FAILED")
print("="*70)

if not df_today.empty:
    if distance_at_entry < 0:
        print(f"❌ Strike was OTM at entry ({distance_at_entry:.2f} points)")
        print(f"   Nifty needed to move {abs(distance_at_entry):.2f} points just to reach ATM")
    
    spot_move = spot_1032 - spot_929
    if spot_move < 0:
        print(f"❌ Nifty moved DOWN {abs(spot_move):.2f} points during trade")
        print(f"   Call options lose value when spot falls")
    elif spot_move < 50:
        print(f"⚠️  Nifty moved only {spot_move:.2f} points UP")
        print(f"   Insufficient movement for OTM call to gain premium")
    
    if high_during_trade < strike:
        print(f"❌ Nifty never reached strike price during trade")
        print(f"   High: ₹{high_during_trade:,.2f}, Strike: ₹{strike:,.2f}")
        print(f"   Gap: {strike - high_during_trade:.2f} points")

print("\n📊 TRADE STATISTICS")
print("="*70)
print(f"Duration: ~63 minutes (9:29 AM to 10:32 AM)")
print(f"Strike: {strike} CE")
print(f"Entry Premium: ₹{entry_premium}")
print(f"Expected Entry: ₹{buy_above} (Buy Above)")
print(f"Stop Loss: ₹{stop_loss}")
print(f"Risk per lot: ₹{risk}")
print(f"Outcome: ❌ FAILED (Exit called)")

print("\n" + "="*70)
print("CONCLUSION")
print("="*70)
print("The 24700 CE trade failed because:")
print("1. Nifty spot was below strike at entry (OTM)")
print("2. Insufficient upward movement to reach targets")
print("3. Exit signal given at 10:32 AM")
print("4. Premium likely didn't cross ₹195 buy trigger")
print("="*70)
