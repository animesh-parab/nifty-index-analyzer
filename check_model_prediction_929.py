"""
Check what our model predicted at 9:29 AM on March 6, 2026
"""

import pandas as pd
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

print("="*70)
print("MODEL ANALYSIS AT 9:29 AM - MARCH 6, 2026")
print("="*70)

# Read prediction log
try:
    df = pd.read_csv('prediction_log.csv')
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Filter for today
    today = datetime.now(IST).date()
    df_today = df[df['timestamp'].dt.date == today]
    
    # Find prediction closest to 9:29 AM
    target_time = datetime(today.year, today.month, today.day, 9, 29, tzinfo=IST)
    
    # Remove timezone from df timestamps for comparison
    df_today['timestamp'] = df_today['timestamp'].dt.tz_localize(None)
    target_time_naive = target_time.replace(tzinfo=None)
    
    # Find closest prediction
    time_diff = abs((df_today['timestamp'] - target_time_naive).dt.total_seconds())
    closest_idx = time_diff.idxmin()
    prediction = df_today.loc[closest_idx]
    
    pred_time = prediction['timestamp']
    direction = prediction['final_direction']
    confidence = prediction['confidence']
    entry_price = prediction['entry_price']
    rsi = prediction['rsi_14']
    macd = prediction['macd_value']
    vix = prediction['vix']
    
    print(f"\n📊 PREDICTION AT {pred_time.strftime('%H:%M:%S')}")
    print("="*70)
    print(f"Direction: {direction}")
    print(f"Confidence: {confidence}%")
    print(f"Nifty Spot: ₹{entry_price:,.2f}")
    
    print(f"\n📈 TECHNICAL INDICATORS")
    print("="*70)
    print(f"RSI: {rsi:.1f}")
    print(f"MACD: {macd:.2f}")
    print(f"VIX: {vix:.2f}")
    
    # Analyze what this means for the trade
    print(f"\n🎯 MODEL'S VIEW ON THE TRADE")
    print("="*70)
    
    if direction == "BULLISH":
        print("✅ Model was BULLISH")
        print("   → Supports CALL option trade")
        print(f"   → Confidence: {confidence}%")
        
        if confidence >= 60:
            print("   → HIGH confidence - Good setup")
        elif confidence >= 50:
            print("   → MODERATE confidence - Proceed with caution")
        else:
            print("   → LOW confidence - Risky trade")
            
    elif direction == "BEARISH":
        print("❌ Model was BEARISH")
        print("   → CONTRADICTS CALL option trade")
        print(f"   → Confidence: {confidence}%")
        print("   → Should have avoided CALL trade")
        print("   → Consider PUT instead")
        
    else:  # SIDEWAYS
        print("⚠️  Model was SIDEWAYS")
        print("   → No clear direction")
        print(f"   → Confidence: {confidence}%")
        print("   → Risky for directional trades")
        print("   → Better to wait for clear signal")
    
    # RSI analysis
    print(f"\n📊 RSI ANALYSIS")
    print("="*70)
    if rsi < 30:
        print(f"RSI: {rsi:.1f} - OVERSOLD")
        print("   → Bullish reversal likely")
        print("   → Good for CALL trades")
    elif rsi > 70:
        print(f"RSI: {rsi:.1f} - OVERBOUGHT")
        print("   → Bearish reversal likely")
        print("   → Bad for CALL trades")
    elif 40 < rsi < 60:
        print(f"RSI: {rsi:.1f} - NEUTRAL")
        print("   → No strong momentum")
        print("   → Wait for clearer signal")
    else:
        print(f"RSI: {rsi:.1f}")
    
    # VIX analysis
    print(f"\n📊 VIX ANALYSIS")
    print("="*70)
    if vix > 20:
        print(f"VIX: {vix:.2f} - HIGH")
        print("   → High volatility/fear")
        print("   → Risky for option buying")
        print("   → Premium decay faster")
    elif vix < 13:
        print(f"VIX: {vix:.2f} - LOW")
        print("   → Low volatility")
        print("   → Good for option buying")
        print("   → Cheaper premiums")
    else:
        print(f"VIX: {vix:.2f} - NORMAL")
        print("   → Moderate volatility")
    
    # Check if we have trade signal data
    print(f"\n🎯 TRADE SIGNAL SCANNER")
    print("="*70)
    
    # Check predictions around 9:29 for any CALL setup
    df_morning = df_today[(df_today['timestamp'].dt.hour == 9) & 
                          (df_today['timestamp'].dt.minute >= 25) & 
                          (df_today['timestamp'].dt.minute <= 35)]
    
    if len(df_morning) > 0:
        bullish_count = len(df_morning[df_morning['final_direction'] == 'BULLISH'])
        bearish_count = len(df_morning[df_morning['final_direction'] == 'BEARISH'])
        sideways_count = len(df_morning[df_morning['final_direction'] == 'SIDEWAYS'])
        
        print(f"Predictions between 9:25-9:35:")
        print(f"  BULLISH: {bullish_count}")
        print(f"  BEARISH: {bearish_count}")
        print(f"  SIDEWAYS: {sideways_count}")
        
        if bullish_count > bearish_count:
            print("\n✅ Majority BULLISH - Supports CALL trade")
        elif bearish_count > bullish_count:
            print("\n❌ Majority BEARISH - Contradicts CALL trade")
        else:
            print("\n⚠️  Mixed signals - No clear direction")
    
    # Final verdict
    print(f"\n" + "="*70)
    print("FINAL VERDICT")
    print("="*70)
    
    if direction == "BULLISH" and confidence >= 60:
        print("✅ MODEL SUPPORTS THE TRADE")
        print("   → BULLISH direction")
        print(f"   → High confidence ({confidence}%)")
        print("   → CALL trade aligned with model")
    elif direction == "BULLISH" and confidence < 60:
        print("⚠️  MODEL WEAKLY SUPPORTS THE TRADE")
        print("   → BULLISH direction")
        print(f"   → Low confidence ({confidence}%)")
        print("   → Proceed with caution")
    elif direction == "BEARISH":
        print("❌ MODEL CONTRADICTS THE TRADE")
        print("   → BEARISH direction")
        print(f"   → Confidence: {confidence}%")
        print("   → CALL trade was against model signal")
        print("   → This explains why trade failed")
    else:
        print("⚠️  MODEL WAS NEUTRAL")
        print("   → SIDEWAYS direction")
        print(f"   → Low confidence ({confidence}%)")
        print("   → No clear signal for CALL trade")
    
    # Check actual outcome
    outcome = prediction.get('actual_outcome', None)
    if pd.notna(outcome):
        print(f"\n📊 ACTUAL OUTCOME (60-min later)")
        print("="*70)
        if outcome == 1:
            print("✅ Market went UP")
            if direction == "BULLISH":
                print("   → Model was CORRECT")
            else:
                print("   → Model was WRONG")
        elif outcome == -1:
            print("❌ Market went DOWN")
            if direction == "BEARISH":
                print("   → Model was CORRECT")
            else:
                print("   → Model was WRONG")
        else:
            print("↔️  Market was SIDEWAYS")
            if direction == "SIDEWAYS":
                print("   → Model was CORRECT")
            else:
                print("   → Model was WRONG")
    else:
        print(f"\n⏳ Outcome not yet available (need 60 minutes)")
    
    print("="*70)
    
except FileNotFoundError:
    print("❌ ERROR: prediction_log.csv not found")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
