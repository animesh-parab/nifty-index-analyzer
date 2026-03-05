"""
Trade Signal Scanner - Locked Rules (Strict Version)
Scans for CALL and PUT setups based on verified backtest rules
"""

import pandas as pd
import numpy as np
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")


def calculate_rsi(prices, period=14):
    """Calculate RSI indicator"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_atr(high, low, close, period=14):
    """Calculate ATR indicator"""
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr


def generate_trade_signal(
    current_price: float,
    last_20_candles: pd.DataFrame,
    rsi: float,
    atr: float,
    current_time: datetime,
    prev_rsi: float = None
) -> dict:
    """
    LOCKED STRICT RULES - Verified with 8 signals, 50% win rate, +50 points
    
    CALL Setup:
    - Position < 0.25, RSI < 45, RSI rising (required)
    - Distance to support < 25, R:R > 2.0, Candles > 3
    - Confluence 7/7, Time filter
    
    PUT Setup:
    - Position > 0.7, RSI > 60, Distance to resistance < 5
    - Distance to support > 100, Rally > 80, R:R > 2.0
    - Confluence 7/7, Time filter
    """
    
    recent_high = last_20_candles['high'].max()
    recent_low = last_20_candles['low'].min()
    range_size = recent_high - recent_low
    
    if range_size == 0:
        return {"signal": "NO_TRADE", "reason": "No range"}
    
    position_in_range = (current_price - recent_low) / range_size
    distance_to_support = current_price - recent_low
    distance_to_resistance = recent_high - current_price
    
    # Time filter: 10:00-12:00 or 1:30-2:30
    time_minutes = current_time.hour * 60 + current_time.minute
    in_high_confidence_zone = (600 <= time_minutes <= 720) or (810 <= time_minutes <= 870)
    
    if not in_high_confidence_zone:
        return {"signal": "NO_TRADE", "reason": "Outside trading hours (10:00-12:00, 1:30-2:30)"}
    
    # Check RSI direction
    rsi_rising = None
    if prev_rsi is not None:
        rsi_rising = rsi > prev_rsi
    
    # Count candles since recent low
    candles_since_low = 0
    for i in range(len(last_20_candles) - 1, -1, -1):
        if last_20_candles.iloc[i]['low'] == recent_low:
            candles_since_low = len(last_20_candles) - 1 - i
            break
    
    # ========================================
    # CALL SETUP (STRICT)
    # ========================================
    
    if position_in_range < 0.25:
        # ATR-based stop
        stop_loss_raw = recent_low - (atr * 0.5)
        min_stop_distance = max(atr * 0.3, 5)
        
        if (current_price - stop_loss_raw) < min_stop_distance:
            stop_loss = current_price - min_stop_distance
        else:
            stop_loss = stop_loss_raw
        
        risk = current_price - stop_loss
        
        if risk < 5:
            return {"signal": "NO_TRADE", "reason": f"Stop too tight ({risk:.2f})"}
        
        target_1 = current_price + (atr * 1.0)
        target_2 = current_price + (atr * 1.5)
        reward = target_2 - current_price
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        # STRICT CALL CONDITIONS
        conditions = {
            'position < 0.25': position_in_range < 0.25,
            'rsi < 45': rsi < 45,
            'distance_to_support < 25': distance_to_support < 25,
            'rr > 2.0': risk_reward_ratio > 2.0,
            'time_filter': in_high_confidence_zone,
            'candles_since_low > 3': candles_since_low > 3,
            'rsi_rising': rsi_rising if rsi_rising is not None else False
        }
        
        confluence_score = sum(conditions.values())
        
        # Require 7/7 conditions
        if confluence_score < 7:
            return {"signal": "NO_TRADE", "reason": f"CALL confluence {confluence_score}/7"}
        
        # Check all critical conditions
        if (
            position_in_range < 0.25 and
            rsi < 45 and
            distance_to_support < 25 and
            risk_reward_ratio > 2.0 and
            candles_since_low > 3 and
            rsi_rising
        ):
            return {
                "signal": "BUY",
                "entry": round(current_price, 2),
                "stop_loss": round(stop_loss, 2),
                "target_1": round(target_1, 2),
                "target_2": round(target_2, 2),
                "risk": round(risk, 2),
                "reward": round(reward, 2),
                "risk_reward_ratio": round(risk_reward_ratio, 2),
                "confidence": 70 + (confluence_score * 3),
                "confluence_score": confluence_score,
                "total_conditions": 7,
                "setup_type": "SUPPORT_BOUNCE",
                "position_in_range": round(position_in_range, 3),
                "recent_high": round(recent_high, 2),
                "recent_low": round(recent_low, 2),
                "rsi": round(rsi, 1),
                "rsi_rising": rsi_rising,
                "candles_since_low": candles_since_low,
                "time": current_time.strftime("%H:%M:%S")
            }
    
    # ========================================
    # PUT SETUP (STRICT)
    # ========================================
    
    if position_in_range > 0.7:
        # Breakout protection
        if current_price > recent_high + 10:
            return {"signal": "NO_TRADE", "reason": "Breakout detected"}
        
        # ATR-based stop
        stop_loss_raw = recent_high + (atr * 0.5)
        min_stop_distance = max(atr * 0.3, 5)
        
        if (stop_loss_raw - current_price) < min_stop_distance:
            stop_loss = current_price + min_stop_distance
        else:
            stop_loss = stop_loss_raw
        
        risk = stop_loss - current_price
        
        if risk < 5:
            return {"signal": "NO_TRADE", "reason": f"Stop too tight ({risk:.2f})"}
        
        target_1 = current_price - (atr * 1.0)
        target_2 = current_price - (atr * 1.5)
        reward = current_price - target_2
        risk_reward_ratio = reward / risk if risk > 0 else 0
        rally_size = current_price - recent_low
        
        # STRICT PUT CONDITIONS
        confluence_score = sum([
            position_in_range > 0.7,
            distance_to_resistance < 5,
            distance_to_support > 100,
            rsi > 60,
            rally_size > 80,
            risk_reward_ratio > 2.0,
            in_high_confidence_zone
        ])
        
        # Require 7/7 conditions
        if confluence_score < 7:
            return {"signal": "NO_TRADE", "reason": f"PUT confluence {confluence_score}/7"}
        
        if (
            distance_to_resistance < 5 and
            distance_to_support > 100 and
            rsi > 60 and
            rally_size > 80 and
            risk_reward_ratio > 2.0
        ):
            return {
                "signal": "SELL",
                "entry": round(current_price, 2),
                "stop_loss": round(stop_loss, 2),
                "target_1": round(target_1, 2),
                "target_2": round(target_2, 2),
                "risk": round(risk, 2),
                "reward": round(reward, 2),
                "risk_reward_ratio": round(risk_reward_ratio, 2),
                "confidence": 75 + (confluence_score * 2),
                "confluence_score": confluence_score,
                "total_conditions": 7,
                "setup_type": "RESISTANCE_REJECTION",
                "position_in_range": round(position_in_range, 3),
                "recent_high": round(recent_high, 2),
                "recent_low": round(recent_low, 2),
                "rsi": round(rsi, 1),
                "rally_size": round(rally_size, 2),
                "time": current_time.strftime("%H:%M:%S")
            }
    
    return {"signal": "NO_TRADE", "reason": f"No setup (position={position_in_range:.2f})"}


def scan_for_signals(candle_data: pd.DataFrame) -> dict:
    """
    Scan current market data for trade signals
    
    Args:
        candle_data: DataFrame with columns ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    
    Returns:
        dict with signal information or NO_TRADE
    """
    if len(candle_data) < 20:
        return {"signal": "NO_TRADE", "reason": "Insufficient data (need 20+ candles)"}
    
    # Ensure columns are lowercase
    candle_data.columns = [col.lower() for col in candle_data.columns]
    
    # Calculate indicators
    candle_data['rsi'] = calculate_rsi(candle_data['close'])
    candle_data['atr'] = calculate_atr(candle_data['high'], candle_data['low'], candle_data['close'])
    
    # Drop NaN rows
    candle_data = candle_data.dropna()
    
    if len(candle_data) < 20:
        return {"signal": "NO_TRADE", "reason": "Insufficient data after indicator calculation"}
    
    # Get current candle (last row)
    current_candle = candle_data.iloc[-1]
    current_time = datetime.now(IST)
    
    # Get last 20 candles (excluding current)
    last_20 = candle_data.iloc[-21:-1]
    
    # Get previous RSI
    prev_rsi = candle_data.iloc[-2]['rsi'] if len(candle_data) > 1 else None
    
    # Generate signal
    signal = generate_trade_signal(
        current_price=current_candle['close'],
        last_20_candles=last_20,
        rsi=current_candle['rsi'],
        atr=current_candle['atr'],
        current_time=current_time,
        prev_rsi=prev_rsi
    )
    
    return signal
