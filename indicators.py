"""
indicators.py
Calculates all technical indicators from OHLCV data.
RSI, MACD, EMA, ATR, Bollinger Bands, VWAP, Supertrend
"""

import pandas as pd
import numpy as np
from config import (
    EMA_SHORT, EMA_MID, EMA_LONG, EMA_200,
    RSI_PERIOD, MACD_FAST, MACD_SLOW, MACD_SIGNAL,
    BB_PERIOD, BB_STD, ATR_PERIOD
)


def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def calculate_rsi(series: pd.Series, period: int = RSI_PERIOD) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calculate_macd(series: pd.Series) -> pd.DataFrame:
    fast = calculate_ema(series, MACD_FAST)
    slow = calculate_ema(series, MACD_SLOW)
    macd_line = fast - slow
    signal_line = calculate_ema(macd_line, MACD_SIGNAL)
    histogram = macd_line - signal_line
    return pd.DataFrame({
        "macd": macd_line,
        "signal": signal_line,
        "histogram": histogram
    })


def calculate_bollinger_bands(series: pd.Series, period: int = BB_PERIOD, std: float = BB_STD) -> pd.DataFrame:
    sma = series.rolling(window=period).mean()
    stddev = series.rolling(window=period).std()
    upper = sma + std * stddev
    lower = sma - std * stddev
    bandwidth = (upper - lower) / sma
    return pd.DataFrame({
        "bb_upper": upper,
        "bb_mid": sma,
        "bb_lower": lower,
        "bb_bandwidth": bandwidth
    })


def calculate_atr(df: pd.DataFrame, period: int = ATR_PERIOD) -> pd.Series:
    high = df["high"]
    low = df["low"]
    close = df["close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)
    return tr.ewm(span=period, adjust=False).mean()


def calculate_vwap(df: pd.DataFrame) -> pd.Series:
    """VWAP - resets each day."""
    df = df.copy()
    df["date"] = df.index.date
    df["typical_price"] = (df["high"] + df["low"] + df["close"]) / 3
    df["tp_vol"] = df["typical_price"] * df["volume"]
    df["cum_tp_vol"] = df.groupby("date")["tp_vol"].cumsum()
    df["cum_vol"] = df.groupby("date")["volume"].cumsum()
    vwap = df["cum_tp_vol"] / df["cum_vol"]
    return vwap


def calculate_supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> pd.DataFrame:
    """Supertrend indicator."""
    hl2 = (df["high"] + df["low"]) / 2
    atr = calculate_atr(df, period)

    upper_band = hl2 + multiplier * atr
    lower_band = hl2 - multiplier * atr

    supertrend = pd.Series(index=df.index, dtype=float)
    direction = pd.Series(index=df.index, dtype=int)

    for i in range(1, len(df)):
        # Upper band
        if upper_band.iloc[i] < upper_band.iloc[i - 1] or df["close"].iloc[i - 1] > upper_band.iloc[i - 1]:
            upper_band.iloc[i] = upper_band.iloc[i]
        else:
            upper_band.iloc[i] = upper_band.iloc[i - 1]

        # Lower band
        if lower_band.iloc[i] > lower_band.iloc[i - 1] or df["close"].iloc[i - 1] < lower_band.iloc[i - 1]:
            lower_band.iloc[i] = lower_band.iloc[i]
        else:
            lower_band.iloc[i] = lower_band.iloc[i - 1]

        # Direction
        if df["close"].iloc[i] > upper_band.iloc[i - 1]:
            direction.iloc[i] = 1   # Uptrend
            supertrend.iloc[i] = lower_band.iloc[i]
        elif df["close"].iloc[i] < lower_band.iloc[i - 1]:
            direction.iloc[i] = -1  # Downtrend
            supertrend.iloc[i] = upper_band.iloc[i]
        else:
            direction.iloc[i] = direction.iloc[i - 1]
            supertrend.iloc[i] = lower_band.iloc[i] if direction.iloc[i] == 1 else upper_band.iloc[i]

    return pd.DataFrame({"supertrend": supertrend, "st_direction": direction})


def detect_candlestick_patterns(df: pd.DataFrame) -> dict:
    """Detect common candlestick patterns on last few candles."""
    if len(df) < 3:
        return {}

    patterns = {}
    last = df.iloc[-1]
    prev = df.iloc[-2]
    prev2 = df.iloc[-3]

    body = abs(last["close"] - last["open"])
    range_ = last["high"] - last["low"]
    upper_wick = last["high"] - max(last["close"], last["open"])
    lower_wick = min(last["close"], last["open"]) - last["low"]

    if range_ > 0:
        body_pct = body / range_

        # Doji
        if body_pct < 0.1:
            patterns["Doji"] = "Indecision - possible reversal"

        # Hammer (bullish)
        if lower_wick > 2 * body and upper_wick < body and last["close"] > last["open"]:
            patterns["Hammer"] = "Bullish reversal signal"

        # Shooting Star (bearish)
        if upper_wick > 2 * body and lower_wick < body and last["close"] < last["open"]:
            patterns["Shooting Star"] = "Bearish reversal signal"

        # Marubozu (strong trend)
        if body_pct > 0.9:
            if last["close"] > last["open"]:
                patterns["Bullish Marubozu"] = "Strong bullish momentum"
            else:
                patterns["Bearish Marubozu"] = "Strong bearish momentum"

    # Engulfing
    if (last["open"] < prev["close"] and last["close"] > prev["open"]
            and last["close"] > last["open"]):
        patterns["Bullish Engulfing"] = "Strong bullish reversal"

    if (last["open"] > prev["close"] and last["close"] < prev["open"]
            and last["close"] < last["open"]):
        patterns["Bearish Engulfing"] = "Strong bearish reversal"

    return patterns


def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate all indicators and return enriched dataframe."""
    if df.empty or len(df) < 30:
        return df

    df = df.copy()

    # EMAs
    df["ema9"] = calculate_ema(df["close"], EMA_SHORT)
    df["ema21"] = calculate_ema(df["close"], EMA_MID)
    df["ema50"] = calculate_ema(df["close"], EMA_LONG)
    df["ema200"] = calculate_ema(df["close"], EMA_200)

    # RSI
    df["rsi"] = calculate_rsi(df["close"], RSI_PERIOD)

    # MACD
    macd_df = calculate_macd(df["close"])
    df["macd"] = macd_df["macd"]
    df["macd_signal"] = macd_df["signal"]
    df["macd_hist"] = macd_df["histogram"]

    # Bollinger Bands
    bb_df = calculate_bollinger_bands(df["close"])
    df["bb_upper"] = bb_df["bb_upper"]
    df["bb_mid"] = bb_df["bb_mid"]
    df["bb_lower"] = bb_df["bb_lower"]
    df["bb_bandwidth"] = bb_df["bb_bandwidth"]

    # ATR
    df["atr"] = calculate_atr(df, ATR_PERIOD)

    # VWAP
    try:
        df["vwap"] = calculate_vwap(df)
    except Exception:
        df["vwap"] = df["close"].rolling(20).mean()

    # Supertrend
    try:
        st_df = calculate_supertrend(df)
        df["supertrend"] = st_df["supertrend"]
        df["st_direction"] = st_df["st_direction"]
    except Exception:
        df["supertrend"] = np.nan
        df["st_direction"] = 0

    return df


def get_indicator_summary(df: pd.DataFrame) -> dict:
    """
    Generate a human-readable summary of current indicator signals.
    Returns dict with signal, value, and interpretation for each indicator.
    """
    if df.empty or len(df) < 5:
        return {}

    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) >= 2 else last

    summary = {}

    # RSI
    rsi = last.get("rsi", 50)
    if rsi >= 70:
        rsi_signal = "OVERBOUGHT"
    elif rsi <= 30:
        rsi_signal = "OVERSOLD"
    elif rsi >= 55:
        rsi_signal = "BULLISH"
    elif rsi <= 45:
        rsi_signal = "BEARISH"
    else:
        rsi_signal = "NEUTRAL"
    summary["RSI"] = {"value": round(rsi, 2), "signal": rsi_signal}

    # MACD
    macd = last.get("macd", 0)
    macd_sig = last.get("macd_signal", 0)
    macd_hist = last.get("macd_hist", 0)
    prev_hist = prev.get("macd_hist", 0)
    if macd > macd_sig and macd_hist > 0 and macd_hist > prev_hist:
        macd_signal = "STRONG BULLISH"
    elif macd > macd_sig:
        macd_signal = "BULLISH"
    elif macd < macd_sig and macd_hist < 0 and macd_hist < prev_hist:
        macd_signal = "STRONG BEARISH"
    elif macd < macd_sig:
        macd_signal = "BEARISH"
    else:
        macd_signal = "NEUTRAL"
    summary["MACD"] = {"value": round(macd, 2), "signal": macd_signal, "histogram": round(macd_hist, 2)}

    # EMA Trend
    close = last["close"]
    ema9 = last.get("ema9", close)
    ema21 = last.get("ema21", close)
    ema50 = last.get("ema50", close)
    if close > ema9 > ema21 > ema50:
        ema_signal = "STRONG UPTREND"
    elif close > ema21 and ema9 > ema21:
        ema_signal = "UPTREND"
    elif close < ema9 < ema21 < ema50:
        ema_signal = "STRONG DOWNTREND"
    elif close < ema21 and ema9 < ema21:
        ema_signal = "DOWNTREND"
    else:
        ema_signal = "SIDEWAYS"
    summary["EMA_Trend"] = {"value": round(close, 2), "signal": ema_signal,
                             "ema9": round(ema9, 2), "ema21": round(ema21, 2), "ema50": round(ema50, 2)}

    # Bollinger Bands
    bb_upper = last.get("bb_upper", 0)
    bb_lower = last.get("bb_lower", 0)
    bb_mid = last.get("bb_mid", 0)
    bb_bw = last.get("bb_bandwidth", 0)
    if close >= bb_upper:
        bb_signal = "OVERBOUGHT / BREAKOUT UP"
    elif close <= bb_lower:
        bb_signal = "OVERSOLD / BREAKOUT DOWN"
    elif bb_bw < 0.02:
        bb_signal = "SQUEEZE (BIG MOVE IMMINENT)"
    elif close > bb_mid:
        bb_signal = "UPPER HALF - BULLISH BIAS"
    else:
        bb_signal = "LOWER HALF - BEARISH BIAS"
    summary["Bollinger_Bands"] = {"value": round(close, 2), "signal": bb_signal,
                                   "upper": round(bb_upper, 2), "lower": round(bb_lower, 2)}

    # ATR (volatility)
    atr = last.get("atr", 0)
    atr_pct = (atr / close * 100) if close > 0 else 0
    if atr_pct > 0.5:
        atr_signal = "HIGH VOLATILITY"
    elif atr_pct < 0.2:
        atr_signal = "LOW VOLATILITY"
    else:
        atr_signal = "NORMAL VOLATILITY"
    summary["ATR"] = {"value": round(atr, 2), "signal": atr_signal, "pct": round(atr_pct, 3)}

    # VWAP
    vwap = last.get("vwap", close)
    if close > vwap * 1.001:
        vwap_signal = "ABOVE VWAP (Bullish)"
    elif close < vwap * 0.999:
        vwap_signal = "BELOW VWAP (Bearish)"
    else:
        vwap_signal = "AT VWAP (Neutral)"
    summary["VWAP"] = {"value": round(vwap, 2), "signal": vwap_signal}

    # Supertrend
    st_dir = last.get("st_direction", 0)
    if st_dir == 1:
        st_signal = "BULLISH (Price above Supertrend)"
    elif st_dir == -1:
        st_signal = "BEARISH (Price below Supertrend)"
    else:
        st_signal = "NEUTRAL"
    summary["Supertrend"] = {"signal": st_signal}

    return summary
