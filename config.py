"""
config.py — Central configuration for Nifty AI Prediction Dashboard
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── API KEYS ──────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ── AI MODELS ─────────────────────────────────────────────────────────────────
GROQ_MODEL = "llama-3.3-70b-versatile"  # Llama 3.3 70B on Groq
GEMINI_MODEL = "gemini-1.5-flash"  # Gemini 1.5 Flash

# ── MARKET SETTINGS ───────────────────────────────────────────────────────────
MARKET_OPEN_HOUR   = 9
MARKET_OPEN_MIN    = 15
MARKET_CLOSE_HOUR  = 15
MARKET_CLOSE_MIN   = 30
TIMEZONE           = "Asia/Kolkata"

# ── NIFTY SETTINGS ────────────────────────────────────────────────────────────
NIFTY_SYMBOL_YF    = "^NSEI"          # yfinance symbol
NIFTY_SYMBOL_NSE   = "NIFTY 50"
BANKNIFTY_SYMBOL_YF = "^NSEBANK"      # Bank Nifty yfinance symbol
BANKNIFTY_SYMBOL_NSE = "NIFTY BANK"
VIX_SYMBOL_YF      = "^INDIAVIX"
NIFTY_LOT_SIZE     = 75               # Current Nifty lot size
BANKNIFTY_LOT_SIZE = 15               # Current Bank Nifty lot size

# Index symbols for Angel One
ANGEL_NIFTY_TOKEN = "99926000"        # Nifty 50 token
ANGEL_BANKNIFTY_TOKEN = "99926009"    # Bank Nifty token

# ── DATA FETCH SETTINGS ───────────────────────────────────────────────────────
REFRESH_INTERVAL_SECONDS = 60         # 1 min auto-refresh
CANDLE_INTERVAL          = "5m"       # Candle timeframe for chart
CANDLE_PERIOD            = "5d"       # How much history to show (increased from 2d for better volatility forecasting)
CROSS_VALIDATE_THRESHOLD = 0.002      # 0.2% max difference allowed between sources

# ── TECHNICAL INDICATOR SETTINGS ─────────────────────────────────────────────
EMA_SHORT   = 9
EMA_MID     = 21
EMA_LONG    = 50
EMA_200     = 200
RSI_PERIOD  = 14
MACD_FAST   = 12
MACD_SLOW   = 26
MACD_SIGNAL = 9
BB_PERIOD   = 20
BB_STD      = 2
ATR_PERIOD  = 14

# ── NSE API HEADERS (mimic browser to avoid blocks) ──────────────────────────
NSE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept":          "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer":         "https://www.nseindia.com/",
    "Connection":      "keep-alive",
}

# ── NEWS SOURCES ──────────────────────────────────────────────────────────────
NEWS_FEEDS = [
    {
        "name":  "Economic Times Markets",
        "url":   "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "weight": 1.0,
    },
    {
        "name":  "MoneyControl News",
        "url":   "https://www.moneycontrol.com/rss/MCtopnews.xml",
        "weight": 0.9,
    },
    {
        "name":  "LiveMint Markets",
        "url":   "https://www.livemint.com/rss/markets",
        "weight": 0.8,
    },
    {
        "name":  "Business Standard Markets",
        "url":   "https://www.business-standard.com/rss/markets-106.rss",
        "weight": 0.8,
    },
]

# ── PREDICTION SETTINGS ───────────────────────────────────────────────────────
PREDICTION_HORIZONS = [5, 15, 30, 40]   # minutes
CONFIDENCE_THRESHOLD_HIGH = 70           # % above which we show strong signal
CONFIDENCE_THRESHOLD_MED  = 50           # % above which we show moderate signal

# ── VIX INTERPRETATION ────────────────────────────────────────────────────────
VIX_LOW    = 13    # Below this: sell premium
VIX_HIGH   = 20   # Above this: buy options / caution

# ── PCR INTERPRETATION ────────────────────────────────────────────────────────
PCR_BULLISH = 1.2   # Above: bullish
PCR_BEARISH = 0.8   # Below: bearish
