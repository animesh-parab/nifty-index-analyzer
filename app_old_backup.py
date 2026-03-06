"""
app.py — Nifty AI Prediction Dashboard
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import pytz
import time

# Auto-refresh every 60 seconds
from streamlit_autorefresh import st_autorefresh

from config import REFRESH_INTERVAL_SECONDS, VIX_LOW, VIX_HIGH, PCR_BULLISH, PCR_BEARISH, CONFIDENCE_THRESHOLD_HIGH, CONFIDENCE_THRESHOLD_MED
from data_fetcher import get_live_nifty_price, get_candle_data, get_india_vix, get_options_chain, get_global_cues, get_market_status, is_market_open
from indicators import calculate_all_indicators, get_indicator_summary, detect_candlestick_patterns
from news_fetcher_scheduled import get_all_news  # Scheduled fetching (9 AM, 12 PM, 3 PM only)
from greeks import get_atm_greeks
# Using Dual-AI Consensus (Groq + Gemini) for validated predictions
from ai_engine_consensus import get_consensus_prediction, get_rule_based_prediction
# Enhanced prediction engine with new indicator scoring
from enhanced_prediction_engine import get_enhanced_prediction, initialize_previous_day_levels
# Prediction logging for XGBoost training
from prediction_logger import log_prediction
# Price alerts with browser notifications
from price_alerts import (
    add_alert, remove_alert, get_active_alerts, 
    get_triggered_alerts, check_alerts, clear_triggered_alerts,
    get_alert_summary
)
# API rate limit monitoring
from api_rate_monitor import (
    get_all_usage_stats, get_usage_summary, 
    check_rate_limit_alerts, get_estimated_daily_usage
)
# Volatility forecasting
from volatility_forecaster import get_volatility_forecast

IST = pytz.timezone("Asia/Kolkata")

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nifty AI Predictor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",  # Show sidebar by default for alerts
)

# ── THEME SYSTEM ─────────────────────────────────────────────────────────────
# Initialize theme in session state
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# Theme configurations
THEMES = {
    'dark': {
        'bg_primary': '#0a0a0f',
        'bg_secondary': '#0d1117',
        'bg_tertiary': '#161b22',
        'border': '#21262d',
        'border_light': '#30363d',
        'text_primary': '#f0f6fc',
        'text_secondary': '#c9d1d9',
        'text_muted': '#8b949e',
        'accent': '#58a6ff',
        'green': '#3fb950',
        'red': '#f85149',
        'yellow': '#d29922',
        'green_bg': '#0d2818',
        'green_bg_alt': '#0f3b2a',
        'red_bg': '#2d0f0f',
        'red_bg_alt': '#3b1515',
        'yellow_bg': '#2d2100',
    },
    'light': {
        'bg_primary': '#ffffff',
        'bg_secondary': '#f6f8fa',
        'bg_tertiary': '#ffffff',
        'border': '#d0d7de',
        'border_light': '#d8dee4',
        'text_primary': '#24292f',
        'text_secondary': '#57606a',
        'text_muted': '#6e7781',
        'accent': '#0969da',
        'green': '#1a7f37',
        'red': '#cf222e',
        'yellow': '#9a6700',
        'green_bg': '#dafbe1',
        'green_bg_alt': '#b4f1c2',
        'red_bg': '#ffebe9',
        'red_bg_alt': '#ffd8d3',
        'yellow_bg': '#fff8c5',
    }
}

theme = THEMES[st.session_state.theme]

# ── STYLES ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;600;700&display=swap');

* {{ box-sizing: border-box; }}

.stApp {{
    background: {theme['bg_primary']};
    font-family: 'Inter', sans-serif;
    transition: background 0.3s ease;
}}

.main .block-container {{
    padding: 1rem 1.5rem;
    max-width: 100%;
}}

/* Header */
.dashboard-header {{
    background: linear-gradient(135deg, {theme['bg_secondary']} 0%, {theme['bg_tertiary']} 100%);
    border: 1px solid {theme['border']};
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: all 0.3s ease;
}}

.header-title {{
    font-family: 'Space Mono', monospace;
    font-size: 1.4rem;
    font-weight: 700;
    color: {theme['accent']};
    letter-spacing: -0.5px;
}}

.header-sub {{
    font-size: 0.75rem;
    color: {theme['text_muted']};
    margin-top: 2px;
}}

/* Price Card */
.price-card {{
    background: linear-gradient(135deg, {theme['bg_secondary']}, {theme['bg_tertiary']});
    border: 1px solid {theme['border_light']};
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
    transition: all 0.3s ease;
}}

.price-value {{
    font-family: 'Space Mono', monospace;
    font-size: 2.4rem;
    font-weight: 700;
    color: {theme['text_primary']};
    letter-spacing: -1px;
}}

.price-change-up {{ color: {theme['green']}; font-size: 1rem; font-weight: 600; }}
.price-change-down {{ color: {theme['red']}; font-size: 1rem; font-weight: 600; }}

/* Metric Cards */
.metric-card {{
    background: {theme['bg_tertiary']};
    border: 1px solid {theme['border']};
    border-radius: 10px;
    padding: 0.9rem 1rem;
    height: 100%;
    transition: all 0.3s ease;
}}

.metric-label {{
    font-size: 0.68rem;
    color: {theme['text_muted']};
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 4px;
}}

.metric-value {{
    font-family: 'Space Mono', monospace;
    font-size: 1.15rem;
    font-weight: 700;
    color: {theme['text_primary']};
}}

/* AI Prediction Card */
.prediction-card {{
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}}

.prediction-bullish {{
    background: linear-gradient(135deg, {theme['green_bg']} 0%, {theme['green_bg_alt']} 100%);
    border: 2px solid {theme['green']};
}}

.prediction-bearish {{
    background: linear-gradient(135deg, {theme['red_bg']} 0%, {theme['red_bg_alt']} 100%);
    border: 2px solid {theme['red']};
}}

.prediction-sideways {{
    background: linear-gradient(135deg, {theme['bg_tertiary']} 0%, {theme['bg_secondary']} 100%);
    border: 2px solid {theme['yellow']};
}}

.pred-direction {{
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: 2px;
}}

.pred-bull {{ color: {theme['green']}; }}
.pred-bear {{ color: {theme['red']}; }}
.pred-side {{ color: {theme['yellow']}; }}

.confidence-bar-container {{
    background: {theme['border']};
    border-radius: 20px;
    height: 10px;
    margin: 8px 0;
    overflow: hidden;
}}

.confidence-bar {{
    height: 100%;
    border-radius: 20px;
    transition: width 0.5s ease;
}}

/* Signal Indicators */
.signal-bullish {{
    background: {theme['green_bg']};
    border: 1px solid {theme['green']};
    color: {theme['green']};
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    display: inline-block;
}}

.signal-bearish {{
    background: {theme['red_bg']};
    border: 1px solid {theme['red']};
    color: {theme['red']};
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    display: inline-block;
}}

.signal-neutral {{
    background: {theme['yellow_bg']};
    border: 1px solid {theme['yellow']};
    color: {theme['yellow']};
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    display: inline-block;
}}

/* Section Headers */
.section-header {{
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: {theme['accent']};
    text-transform: uppercase;
    letter-spacing: 0.15em;
    border-bottom: 1px solid {theme['border']};
    padding-bottom: 6px;
    margin-bottom: 12px;
}}

/* News Items */
.news-item {{
    background: {theme['bg_tertiary']};
    border: 1px solid {theme['border']};
    border-radius: 8px;
    padding: 0.7rem 0.9rem;
    margin-bottom: 6px;
    transition: all 0.3s ease;
}}

.news-title {{ font-size: 0.82rem; color: {theme['text_secondary']}; line-height: 1.4; }}
.news-meta {{ font-size: 0.68rem; color: {theme['text_muted']}; margin-top: 4px; }}

/* Market Status Badge */
.status-open {{
    background: {theme['green_bg']};
    border: 1px solid {theme['green']};
    color: {theme['green']};
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    font-family: 'Space Mono', monospace;
}}

.status-closed {{
    background: {theme['red_bg']};
    border: 1px solid {theme['red']};
    color: {theme['red']};
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    font-family: 'Space Mono', monospace;
}}

.status-preopen {{
    background: {theme['yellow_bg']};
    border: 1px solid {theme['yellow']};
    color: {theme['yellow']};
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    font-family: 'Space Mono', monospace;
}}

/* Global Cues Table */
.cue-row {{
    display: flex;
    justify-content: space-between;
    padding: 5px 0;
    border-bottom: 1px solid {theme['border']};
    font-size: 0.8rem;
}}

.cue-name {{ color: {theme['text_muted']}; }}
.cue-val-up {{ color: {theme['green']}; font-family: 'Space Mono', monospace; font-weight: 600; }}
.cue-val-down {{ color: {theme['red']}; font-family: 'Space Mono', monospace; font-weight: 600; }}

/* Expiry Countdown */
.expiry-badge {{
    background: {theme['bg_tertiary']};
    border: 1px solid {theme['border_light']};
    border-radius: 8px;
    padding: 0.5rem 0.8rem;
    text-align: center;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: {theme['text_muted']};
}}

/* Theme Toggle Button */
.theme-toggle {{
    background: {theme['bg_tertiary']};
    border: 1px solid {theme['border']};
    color: {theme['text_primary']};
    padding: 8px 16px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 600;
    transition: all 0.3s ease;
}}

.theme-toggle:hover {{
    background: {theme['border']};
    transform: scale(1.05);
}}

/* Override Streamlit defaults */
.stMarkdown p {{ color: {theme['text_secondary']}; }}
div[data-testid="stMetricValue"] {{ font-family: 'Space Mono', monospace; color: {theme['text_primary']} !important; }}
.stTabs [data-baseweb="tab"] {{ color: {theme['text_muted']}; }}
.stTabs [aria-selected="true"] {{ color: {theme['accent']} !important; }}

/* Sidebar styling */
section[data-testid="stSidebar"] {{
    background: {theme['bg_secondary']};
    border-right: 1px solid {theme['border']};
}}

section[data-testid="stSidebar"] .stMarkdown {{
    color: {theme['text_secondary']};
}}
</style>
""", unsafe_allow_html=True)


# ── CACHED DATA FETCHERS (cache for 55 seconds to align with 60s refresh) ────
@st.cache_data(ttl=55)
def cached_price(index="NIFTY"):
    return get_live_nifty_price(index)

@st.cache_data(ttl=55)
def cached_candles(index="NIFTY"):
    df = get_candle_data(index)
    if not df.empty:
        df = calculate_all_indicators(df)
    return df

@st.cache_data(ttl=55)
def cached_vix():
    return get_india_vix()

@st.cache_data(ttl=300)  # Options chain: 5-minute cache (rate limit optimization)
def cached_oi():
    return get_options_chain()

@st.cache_data(ttl=300)  # News every 5 min
def cached_news():
    return get_all_news()

@st.cache_data(ttl=120)
def cached_global():
    return get_global_cues()


# ── HELPER: Signal Badge HTML ──────────────────────────────────────────────────
def signal_badge(signal: str) -> str:
    s = signal.upper()
    if any(x in s for x in ["BULL", "UPTREND", "ABOVE", "OVERSOLD", "BUY"]):
        return f'<span class="signal-bullish">{signal}</span>'
    elif any(x in s for x in ["BEAR", "DOWNTREND", "BELOW", "OVERBOUGHT", "SELL"]):
        return f'<span class="signal-bearish">{signal}</span>'
    else:
        return f'<span class="signal-neutral">{signal}</span>'


def generate_simple_explanation(prediction: dict, price: float, vix: float, pcr: float) -> str:
    """Generate simple layman explanation of market direction"""
    direction = prediction.get("direction", "SIDEWAYS")
    confidence = prediction.get("confidence", 0)
    targets = prediction.get("price_targets", {})
    
    # Get target price
    target_price = price
    if targets and "30min" in targets:
        target_price = targets["30min"].get("most_likely", price)
    elif targets and "15min" in targets:
        target_price = targets["15min"].get("most_likely", price)
    
    # Build simple explanation
    if direction == "BULLISH":
        if confidence >= 70:
            explanation = f"📈 <b>Market looks strong!</b> Nifty is likely to move UP towards <b>{target_price:,.0f}</b> points in the next 30 minutes."
        else:
            explanation = f"📊 <b>Slight upward movement expected.</b> Nifty may reach <b>{target_price:,.0f}</b> points, but be cautious."
    elif direction == "BEARISH":
        if confidence >= 70:
            explanation = f"📉 <b>Market looks weak!</b> Nifty is likely to move DOWN towards <b>{target_price:,.0f}</b> points in the next 30 minutes."
        else:
            explanation = f"📊 <b>Slight downward pressure.</b> Nifty may drop to <b>{target_price:,.0f}</b> points, but not confirmed."
    else:
        explanation = f"↔️ <b>Market is sideways.</b> Nifty will likely stay around <b>{price:,.0f}</b> points. Wait for clear direction."
    
    # Add context
    if vix > 20:
        explanation += " <span style='color:#f85149;'>⚠️ High volatility - be extra careful!</span>"
    elif vix < 13:
        explanation += " <span style='color:#3fb950;'>✓ Low volatility - stable market.</span>"
    
    return explanation


def calculate_next_candle_prediction(df_candles: pd.DataFrame, prediction: dict, current_price: float, timeframe_minutes: int) -> dict:
    """Calculate next candle prediction with probability for different timeframes"""
    if df_candles.empty:
        return {
            "direction": "UNKNOWN",
            "points": 0,
            "probability": 0,
            "target_price": current_price,
            "timeframe": timeframe_minutes
        }
    
    # Get recent price action - handle both uppercase and lowercase column names
    recent_candles = df_candles.tail(10)
    
    # Check which column names are present
    if 'Close' in recent_candles.columns:
        close_col, open_col = 'Close', 'Open'
    elif 'close' in recent_candles.columns:
        close_col, open_col = 'close', 'open'
    else:
        # Fallback if columns not found
        return {
            "direction": "UNKNOWN",
            "points": 0,
            "probability": 0,
            "target_price": current_price,
            "timeframe": timeframe_minutes
        }
    
    avg_move = abs(recent_candles[close_col] - recent_candles[open_col]).mean()
    
    # Get AI direction
    direction = prediction.get("direction", "SIDEWAYS")
    confidence = prediction.get("confidence", 50)
    
    # Adjust multiplier based on timeframe
    # Longer timeframes = bigger expected moves
    timeframe_multiplier = {
        5: 0.7,   # Conservative for 5 min
        15: 1.2,  # Moderate for 15 min
        30: 1.8   # Larger for 30 min
    }.get(timeframe_minutes, 1.0)
    
    # Calculate expected move
    if direction == "BULLISH":
        expected_points = avg_move * timeframe_multiplier
        target_price = current_price + expected_points
        # Reduce confidence slightly for longer timeframes (more uncertainty)
        probability = min(confidence - (timeframe_minutes - 5) * 2, 85)
        direction_text = "UP"
    elif direction == "BEARISH":
        expected_points = avg_move * timeframe_multiplier
        target_price = current_price - expected_points
        probability = min(confidence - (timeframe_minutes - 5) * 2, 85)
        direction_text = "DOWN"
    else:
        expected_points = avg_move * timeframe_multiplier * 0.3
        target_price = current_price
        probability = 50
        direction_text = "SIDEWAYS"
    
    return {
        "direction": direction_text,
        "points": abs(expected_points),
        "probability": max(probability, 30),  # Minimum 30% probability
        "target_price": target_price,
        "current_price": current_price,
        "timeframe": timeframe_minutes
    }


# ── MAIN DASHBOARD ─────────────────────────────────────────────────────────────
def main():
    # Initialize session state for start/stop control
    if 'dashboard_running' not in st.session_state:
        st.session_state.dashboard_running = True
    
    now_ist = datetime.now(IST)
    market_status = get_market_status()

    # ── HEADER WITH START/STOP BUTTON ─────────────────────────────────────────
    if "OPEN" in market_status and "PRE" not in market_status:
        status_html = f'<span class="status-open">🟢 {market_status}</span>'
    elif "PRE" in market_status:
        status_html = f'<span class="status-preopen">🟡 {market_status}</span>'
    else:
        status_html = f'<span class="status-closed">🔴 {market_status}</span>'

    # Header with control buttons
    header_col1, header_col2, header_col3, header_col4 = st.columns([3, 1, 1, 1])
    
    with header_col1:
        st.markdown(f"""
        <div class="dashboard-header">
            <div>
                <div class="header-title">⚡ NIFTY AI PREDICTOR</div>
                <div class="header-sub">Multi-source • Cross-validated • AI-powered • Refreshes every 60s</div>
            </div>
            <div style="text-align:right;">
                {status_html}
                <div style="font-size:0.72rem;color:{theme['text_muted']};margin-top:4px;">{now_ist.strftime('%d %b %Y  %H:%M:%S IST')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with header_col2:
        # Index selector
        selected_index = st.selectbox(
            "Index",
            options=["NIFTY", "BANKNIFTY"],
            index=0,
            key="index_selector",
            label_visibility="collapsed",
            help="Select index to track"
        )
    
    with header_col3:
        # Theme toggle
        theme_icon = "☀️" if st.session_state.theme == "dark" else "🌙"
        theme_label = "Light" if st.session_state.theme == "dark" else "Dark"
        if st.button(f"{theme_icon} {theme_label}", use_container_width=True, key="theme_toggle"):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()
    
    with header_col4:
        if st.session_state.dashboard_running:
            if st.button("⏸ PAUSE", use_container_width=True, type="secondary"):
                st.session_state.dashboard_running = False
                st.rerun()
        else:
            if st.button("▶ START", use_container_width=True, type="primary"):
                st.session_state.dashboard_running = True
                st.rerun()
    
    # Only auto-refresh if dashboard is running
    if st.session_state.dashboard_running:
        st_autorefresh(interval=REFRESH_INTERVAL_SECONDS * 1000, key="auto_refresh")

    # ── FETCH ALL DATA ─────────────────────────────────────────────────────────
    with st.spinner(""):
        fetch_start_time = time.time()  # Start timing
        
        # Fetch data ONLY for selected index (not both)
        price_data = cached_price(selected_index)
        df_candles = cached_candles(selected_index)
        vix_data   = cached_vix()
        oi_data    = cached_oi()
        news_data  = cached_news()
        global_cues = cached_global()
        
        fetch_end_time = time.time()  # End timing
        fetch_duration = fetch_end_time - fetch_start_time
        
        # Add timestamp and duration to price_data
        price_data['fetched_at'] = datetime.now(IST).strftime("%H:%M:%S")
        price_data['fetch_duration'] = fetch_duration

    # Indicator summary from candles
    indicator_summary = get_indicator_summary(df_candles) if not df_candles.empty else {}
    patterns = detect_candlestick_patterns(df_candles) if not df_candles.empty else {}
    
    # Initialize previous day levels on first run
    if not df_candles.empty:
        initialize_previous_day_levels(df_candles)

    # ── PRICE ALERTS CHECK ────────────────────────────────────────────────────
    current_price = price_data.get('price', 0)
    if current_price > 0:
        triggered_alerts = check_alerts(current_price)
        
        # Show browser notifications for triggered alerts
        if triggered_alerts:
            for alert in triggered_alerts:
                direction_text = "crossed above" if alert['direction'] == 'above' else "dropped below"
                alert_message = f"🔔 PRICE ALERT: Nifty {direction_text} {alert['price']:,.0f}"
                if alert['note']:
                    alert_message += f" - {alert['note']}"
                
                # Display notification banner
                st.toast(alert_message, icon="🔔")
                
                # Also show as warning banner
                st.warning(f"**{alert_message}**\n\nTriggered at: {datetime.fromisoformat(alert['triggered_at']).strftime('%H:%M:%S IST')}")

    # ── DATA SOURCE WARNING BANNER ─────────────────────────────────────────────
    # Check which sources are being used and show warning if using fallback
    price_source = price_data.get('source', 'Unknown')
    vix_source = vix_data.get('source', 'Unknown')
    
    # Determine if we're using fallback sources
    using_fallback = False
    fallback_sources = []
    
    # Check Nifty price source (NSE is now primary, Angel One is backup)
    if 'yfinance' in price_source.lower():
        using_fallback = True
        fallback_sources.append("Nifty Price (yfinance - 15 min delay)")
    elif 'angel' in price_source.lower():
        # Angel One is backup, show as info (not warning)
        pass
    
    # Note: VIX uses yfinance intentionally (Angel One token is incorrect)
    # NSE is primary for Nifty, so no warning needed
    
    # Show warning banner only if using yfinance (delayed data)
    if using_fallback:
        fallback_list = "<br>• ".join(fallback_sources)
        st.markdown(f"""
        <div style="background: {theme['yellow_bg']}; 
                    border-left: 4px solid {theme['yellow']}; border-radius: 8px; padding: 12px 16px; 
                    margin-bottom: 16px; box-shadow: 0 2px 8px rgba(210, 153, 34, 0.2);">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="font-size: 1.2rem;">⚠️</div>
                <div>
                    <div style="font-size: 0.75rem; color: {theme['yellow']}; font-weight: 600; 
                                letter-spacing: 0.5px; margin-bottom: 4px;">
                        USING DELAYED DATA
                    </div>
                    <div style="font-size: 0.7rem; color: {theme['text_secondary']}; line-height: 1.4;">
                        Real-time sources unavailable. Using backup:<br>
                        • {fallback_list}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Show success banner when using real-time data (NSE or Angel One)
        st.markdown(f"""
        <div style="background: {theme['green_bg']}; 
                    border-left: 4px solid {theme['green']}; border-radius: 8px; padding: 10px 16px; 
                    margin-bottom: 16px; box-shadow: 0 2px 8px rgba(63, 185, 80, 0.2);">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="font-size: 1rem;">✅</div>
                <div style="font-size: 0.7rem; color: {theme['green']}; font-weight: 600; 
                            letter-spacing: 0.5px;">
                    REAL-TIME DATA ACTIVE • {price_source} • Live Market Data
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── TRADE SIGNAL SCANNER ──────────────────────────────────────────────────
    # Scan for CALL/PUT setups every 60 seconds during active hours
    trade_signal = {"signal": "NO_TRADE", "reason": "Not scanned"}
    
    if not df_candles.empty and market_status == "MARKET OPEN":
        from trade_signal_scanner import scan_for_signals
        try:
            trade_signal = scan_for_signals(df_candles)
            
            # Display trade signal alert if BUY or SELL
            if trade_signal['signal'] in ['BUY', 'SELL']:
                signal_type = trade_signal['signal']
                setup_type = trade_signal.get('setup_type', 'UNKNOWN')
                
                # Color scheme
                if signal_type == 'BUY':
                    bg_color = theme['green_bg']
                    border_color = theme['green']
                    text_color = theme['green']
                    icon = "🟢"
                    action_text = "CALL SETUP"
                else:  # SELL
                    bg_color = theme['red_bg']
                    border_color = theme['red']
                    text_color = theme['red']
                    icon = "🔴"
                    action_text = "PUT SETUP"
                
                # Large alert box
                st.markdown(f"""
                <div style="background: {bg_color}; 
                            border: 3px solid {border_color}; 
                            border-radius: 16px; 
                            padding: 24px; 
                            margin-bottom: 20px; 
                            box-shadow: 0 8px 24px rgba(0,0,0,0.3);">
                    <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
                        <div style="font-size: 3rem;">{icon}</div>
                        <div>
                            <div style="font-size: 1.8rem; font-weight: 700; color: {text_color}; 
                                        font-family: 'Space Mono', monospace; letter-spacing: -0.5px;">
                                {action_text} DETECTED
                            </div>
                            <div style="font-size: 0.9rem; color: {theme['text_secondary']}; margin-top: 4px;">
                                {setup_type} • Confluence: {trade_signal.get('confluence_score', 0)}/7 • 
                                Time: {trade_signal.get('time', 'N/A')}
                            </div>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 20px;">
                        <div style="background: {theme['bg_tertiary']}; border-radius: 10px; padding: 14px;">
                            <div style="font-size: 0.7rem; color: {theme['text_muted']}; 
                                        text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                                ENTRY
                            </div>
                            <div style="font-size: 1.6rem; font-weight: 700; color: {text_color}; 
                                        font-family: 'Space Mono', monospace;">
                                ₹{trade_signal.get('entry', 0):,.2f}
                            </div>
                        </div>
                        
                        <div style="background: {theme['bg_tertiary']}; border-radius: 10px; padding: 14px;">
                            <div style="font-size: 0.7rem; color: {theme['text_muted']}; 
                                        text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                                STOP LOSS
                            </div>
                            <div style="font-size: 1.6rem; font-weight: 700; color: {theme['red']}; 
                                        font-family: 'Space Mono', monospace;">
                                ₹{trade_signal.get('stop_loss', 0):,.2f}
                            </div>
                            <div style="font-size: 0.65rem; color: {theme['text_muted']}; margin-top: 4px;">
                                Risk: {trade_signal.get('risk', 0):.2f} pts
                            </div>
                        </div>
                        
                        <div style="background: {theme['bg_tertiary']}; border-radius: 10px; padding: 14px;">
                            <div style="font-size: 0.7rem; color: {theme['text_muted']}; 
                                        text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                                RISK:REWARD
                            </div>
                            <div style="font-size: 1.6rem; font-weight: 700; color: {theme['green']}; 
                                        font-family: 'Space Mono', monospace;">
                                1:{trade_signal.get('risk_reward_ratio', 0):.2f}
                            </div>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-top: 16px;">
                        <div style="background: {theme['bg_tertiary']}; border-radius: 10px; padding: 14px;">
                            <div style="font-size: 0.7rem; color: {theme['text_muted']}; 
                                        text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                                TARGET 1
                            </div>
                            <div style="font-size: 1.4rem; font-weight: 700; color: {theme['green']}; 
                                        font-family: 'Space Mono', monospace;">
                                ₹{trade_signal.get('target_1', 0):,.2f}
                            </div>
                        </div>
                        
                        <div style="background: {theme['bg_tertiary']}; border-radius: 10px; padding: 14px;">
                            <div style="font-size: 0.7rem; color: {theme['text_muted']}; 
                                        text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                                TARGET 2
                            </div>
                            <div style="font-size: 1.4rem; font-weight: 700; color: {theme['green']}; 
                                        font-family: 'Space Mono', monospace;">
                                ₹{trade_signal.get('target_2', 0):,.2f}
                            </div>
                            <div style="font-size: 0.65rem; color: {theme['text_muted']}; margin-top: 4px;">
                                Reward: {trade_signal.get('reward', 0):.2f} pts
                            </div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 16px; padding: 12px; background: {theme['bg_secondary']}; 
                                border-radius: 8px; font-size: 0.75rem; color: {theme['text_secondary']};">
                        <strong>Setup Details:</strong> 
                        Position: {trade_signal.get('position_in_range', 0):.1%} of range • 
                        RSI: {trade_signal.get('rsi', 0):.1f} • 
                        Support: ₹{trade_signal.get('recent_low', 0):,.2f} • 
                        Resistance: ₹{trade_signal.get('recent_high', 0):,.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Also show toast notification
                st.toast(f"{icon} {action_text} DETECTED at ₹{trade_signal.get('entry', 0):,.2f}", icon=icon)
                
        except Exception as e:
            # Silently fail if scanner has issues
            trade_signal = {"signal": "NO_TRADE", "reason": f"Scanner error: {str(e)}"}

    # Greeks
    greeks = {}
    if price_data.get("price", 0) > 0 and oi_data.get("expiry"):
        greeks = get_atm_greeks(price_data["price"], vix_data.get("vix", 15), oi_data.get("expiry", ""))

    # AI Prediction (Enhanced Scoring + Dual-AI Consensus)
    prediction = {}
    try:
        # Try enhanced prediction engine first (with time filter)
        enhanced_pred = get_enhanced_prediction(
            price_data, indicator_summary, df_candles,
            oi_data, vix_data, news_data.get("sentiment", {})
        )
        
        # If time filter blocks prediction, skip entirely
        if enhanced_pred is None:
            prediction = {
                "direction": "BLOCKED",
                "confidence": 0,
                "strength": "N/A",
                "consensus": "TIME_FILTER",
                "agreement": "DISABLED_ZONE",
                "top_3_reasons": ["Prediction disabled during high volatility period"],
                "one_line_summary": "Time filter: Prediction disabled (before 9:30 or after 3:00 PM)",
                "model_used": "Time Filter",
                "generated_at": datetime.now(IST).strftime("%H:%M:%S IST")
            }
        else:
            # Use enhanced prediction
            prediction = enhanced_pred
            
    except Exception as e:
        # Fallback to rule-based if enhanced fails
        try:
            prediction = get_rule_based_prediction(
                indicator_summary, oi_data, vix_data, news_data.get("sentiment", {})
            )
        except Exception as e2:
            prediction = {
                "direction": "ERROR",
                "confidence": 0,
                "strength": "N/A",
                "consensus": "ERROR",
                "agreement": "FALLBACK",
                "top_3_reasons": [str(e)[:100]],
                "one_line_summary": f"Error: {str(e)[:50]}",
                "model_used": "Error Handler",
                "generated_at": datetime.now(IST).strftime("%H:%M:%S IST")
            }

    # Log prediction for XGBoost training (only during market hours with real-time data)
    # Skip logging if prediction was blocked by time filter
    if prediction and price_data.get("price", 0) > 0 and prediction.get("direction") != "BLOCKED":
        try:
            # Get last candle for raw indicator values
            last_candle = df_candles.iloc[-1] if not df_candles.empty else {}
            
            # Prepare indicator values for logging (PCR removed - APIs unreliable)
            indicator_values = {
                'rsi_14': indicator_summary.get('RSI', {}).get('value', 0),
                'macd_value': indicator_summary.get('MACD', {}).get('value', 0),
                'macd_signal': last_candle.get('macd_signal', 0),  # Get numerical value from dataframe
                'ema_9': indicator_summary.get('EMA_Trend', {}).get('ema_9', 0),
                'ema_21': indicator_summary.get('EMA_Trend', {}).get('ema_21', 0),
                'ema_50': indicator_summary.get('EMA_Trend', {}).get('ema_50', 0),
                'bb_position': (last_candle.get('close', 0) - last_candle.get('bb_lower', 0)) / (last_candle.get('bb_upper', 0) - last_candle.get('bb_lower', 0)) if (last_candle.get('bb_upper', 0) - last_candle.get('bb_lower', 0)) > 0 else 0.5,
                'atr_14': indicator_summary.get('ATR', {}).get('value', 0),
                'vix': vix_data.get('vix', 15.0),
                'us_market_change': global_cues.get('S&P 500', {}).get('pct_change', 0),
                'data_source': price_data.get('source', 'Unknown')
                # PCR removed - options APIs unreliable (NSE empty, Angel One failing)
            }
            
            log_prediction(indicator_values, prediction, price_data.get("price", 0))
        except Exception as log_error:
            # Don't let logging errors break the dashboard
            pass

    # ── ROW 1: PRICE + KEY METRICS ─────────────────────────────────────────────
    price = price_data.get("price", 0)
    change = price_data.get("change", 0)
    pct = price_data.get("pct_change", 0)
    chg_color = "#3fb950" if change >= 0 else "#f85149"
    chg_arrow = "▲" if change >= 0 else "▼"
    chg_class = "price-change-up" if change >= 0 else "price-change-down"

    col_price, col_vix, col_pcr, col_maxpain, col_conf = st.columns([2, 1, 1, 1, 1])

    with col_price:
        fetch_time = price_data.get('fetched_at', 'N/A')
        fetch_dur = price_data.get('fetch_duration', 0)
        index_name = "NIFTY 50" if selected_index == "NIFTY" else "BANK NIFTY"
        
        st.markdown(f"""
        <div class="price-card">
            <div class="metric-label">{index_name}</div>
            <div class="price-value">{price:,.2f}</div>
            <div class="{chg_class}">{chg_arrow} {abs(change):,.2f} ({abs(pct):.2f}%)</div>
            <div style="font-size:0.65rem;color:#8b949e;margin-top:4px;">
                Source: {price_data.get('source','N/A')} | {price_data.get('confidence','?')} confidence
            </div>
            <div style="font-size:0.6rem;color:#58a6ff;margin-top:2px;">
                ⏱ Fetched at {fetch_time} ({fetch_dur:.2f}s)
            </div>
        </div>
        """, unsafe_allow_html=True)

    vix = vix_data.get("vix", 0)
    vix_color = "#3fb950" if vix < VIX_LOW else "#f85149" if vix > VIX_HIGH else "#d29922"
    vix_source = vix_data.get("source", "N/A")
    with col_vix:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">India VIX</div>
            <div class="metric-value" style="color:{vix_color}">{vix:.2f}</div>
            <div style="font-size:0.68rem;color:{vix_color};">
                {"🟢 LOW - Sell premium" if vix < VIX_LOW else "🔴 HIGH - Caution" if vix > VIX_HIGH else "🟡 Normal"}
            </div>
            <div style="font-size:0.6rem;color:#8b949e;margin-top:4px;">
                Source: {vix_source}
            </div>
        </div>
        """, unsafe_allow_html=True)

    pcr = oi_data.get("pcr", 0)
    pcr_color = "#3fb950" if pcr > PCR_BULLISH else "#f85149" if pcr < PCR_BEARISH else "#d29922"
    oi_source = oi_data.get("source", "N/A")
    oi_last_updated = oi_data.get("last_updated")
    
    # Calculate time since last update
    if oi_last_updated:
        time_diff = (datetime.now() - oi_last_updated).total_seconds()
        if time_diff < 60:
            time_since = f"{int(time_diff)}s ago"
        else:
            time_since = f"{int(time_diff / 60)}m ago"
    else:
        time_since = "N/A"
    
    with col_pcr:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">PCR</div>
            <div class="metric-value" style="color:{pcr_color}">{pcr:.3f}</div>
            <div style="font-size:0.68rem;color:{pcr_color};">
                {"🐂 Bullish" if pcr > PCR_BULLISH else "🐻 Bearish" if pcr < PCR_BEARISH else "↔ Neutral"}
            </div>
            <div style="font-size:0.6rem;color:#8b949e;margin-top:4px;">
                Updated: {time_since}
            </div>
        </div>
        """, unsafe_allow_html=True)

    max_pain = oi_data.get("max_pain", 0)
    mp_diff = price - max_pain if price and max_pain else 0
    with col_maxpain:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Max Pain</div>
            <div class="metric-value">{max_pain:,.0f}</div>
            <div style="font-size:0.68rem;color:#8b949e;">
                Price is {abs(mp_diff):.0f}pts {'above' if mp_diff > 0 else 'below'}
            </div>
            <div style="font-size:0.6rem;color:#8b949e;margin-top:4px;">
                Source: {oi_source}
            </div>
        </div>
        """, unsafe_allow_html=True)

    confidence = prediction.get("confidence", 0)
    conf_color = "#3fb950" if confidence >= CONFIDENCE_THRESHOLD_HIGH else "#d29922" if confidence >= CONFIDENCE_THRESHOLD_MED else "#f85149"
    with col_conf:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">AI Confidence</div>
            <div class="metric-value" style="color:{conf_color}">{confidence}%</div>
            <div class="confidence-bar-container">
                <div class="confidence-bar" style="width:{confidence}%;background:{conf_color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── NEW: SIMPLE MARKET EXPLANATION ────────────────────────────────────────
    simple_explanation = generate_simple_explanation(prediction, price, vix, pcr)
    st.markdown(f"""
    <div style="background: {theme['bg_tertiary']}; 
                border: 2px solid {theme['accent']}; border-radius: 12px; padding: 20px; 
                margin-bottom: 20px; box-shadow: 0 4px 12px rgba(88, 166, 255, 0.2);">
        <div style="font-size: 0.75rem; color: {theme['accent']}; font-weight: 600; 
                    letter-spacing: 1px; margin-bottom: 10px;">
            💡 SIMPLE MARKET OUTLOOK
        </div>
        <div style="font-size: 1rem; color: {theme['text_primary']}; line-height: 1.6;">
            {simple_explanation}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── NEW: NEXT CANDLE PREDICTION WITH TIMEFRAME SELECTOR ────────────────────
    
    # Add timeframe selector
    st.markdown(f"""
    <div style="font-size: 0.75rem; color: {theme['accent']}; font-weight: 600; 
                letter-spacing: 1px; margin-bottom: 8px; margin-top: 10px;">
        📊 NEXT CANDLE PREDICTION
    </div>
    """, unsafe_allow_html=True)
    
    # Dropdown for timeframe selection
    timeframe_col1, timeframe_col2 = st.columns([1, 3])
    
    with timeframe_col1:
        selected_timeframe = st.selectbox(
            "Timeframe",
            options=[5, 15, 30],
            format_func=lambda x: f"{x} Minutes",
            key="timeframe_selector",
            label_visibility="collapsed"
        )
    
    with timeframe_col2:
        st.markdown(f"""
        <div style="padding: 8px 0; color: {theme['text_muted']}; font-size: 0.75rem;">
            Predicting next <b style="color: {theme['accent']};">{selected_timeframe}-minute</b> candle movement
        </div>
        """, unsafe_allow_html=True)
    
    # Calculate prediction for selected timeframe
    next_candle = calculate_next_candle_prediction(df_candles, prediction, price, selected_timeframe)
    
    # Color based on direction
    if next_candle["direction"] == "UP":
        dir_color = theme['green']
        dir_emoji = "📈"
        dir_arrow = "▲"
    elif next_candle["direction"] == "DOWN":
        dir_color = theme['red']
        dir_emoji = "📉"
        dir_arrow = "▼"
    else:
        dir_color = theme['yellow']
        dir_emoji = "↔️"
        dir_arrow = "→"
    
    prob_color = theme['green'] if next_candle["probability"] >= 70 else theme['yellow'] if next_candle["probability"] >= 50 else theme['red']
    
    col_pred_1, col_pred_2, col_pred_3 = st.columns([1, 1, 1])
    
    with col_pred_1:
        st.markdown(f"""
        <div style="background: {theme['bg_tertiary']}; border: 1px solid {theme['border_light']}; border-radius: 8px; 
                    padding: 16px; text-align: center;">
            <div style="font-size: 0.7rem; color: {theme['text_muted']}; margin-bottom: 8px;">
                DIRECTION
            </div>
            <div style="font-size: 2rem; color: {dir_color}; font-weight: 700;">
                {dir_emoji} {dir_arrow}
            </div>
            <div style="font-size: 0.9rem; color: {dir_color}; font-weight: 600; margin-top: 4px;">
                {next_candle["direction"]}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_pred_2:
        st.markdown(f"""
        <div style="background: {theme['bg_tertiary']}; border: 1px solid {theme['border_light']}; border-radius: 8px; 
                    padding: 16px; text-align: center;">
            <div style="font-size: 0.7rem; color: {theme['text_muted']}; margin-bottom: 8px;">
                EXPECTED MOVE
            </div>
            <div style="font-size: 1.8rem; color: {dir_color}; font-weight: 700;">
                {dir_arrow} {next_candle["points"]:.0f}
            </div>
            <div style="font-size: 0.8rem; color: {theme['text_muted']}; margin-top: 4px;">
                points
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_pred_3:
        st.markdown(f"""
        <div style="background: {theme['bg_tertiary']}; border: 1px solid {theme['border_light']}; border-radius: 8px; 
                    padding: 16px; text-align: center;">
            <div style="font-size: 0.7rem; color: {theme['text_muted']}; margin-bottom: 8px;">
                PROBABILITY
            </div>
            <div style="font-size: 1.8rem; color: {prob_color}; font-weight: 700;">
                {next_candle["probability"]:.0f}%
            </div>
            <div style="font-size: 0.75rem; color: {prob_color}; margin-top: 4px;">
                {"High" if next_candle["probability"] >= 70 else "Medium" if next_candle["probability"] >= 50 else "Low"} confidence
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Target price display
    st.markdown(f"""
    <div style="text-align: center; margin-top: 12px; padding: 12px; 
                background: rgba(88, 166, 255, 0.1); border-radius: 6px;">
        <span style="color: #8b949e; font-size: 0.8rem;">Expected price in {selected_timeframe} minutes: </span>
        <span style="color: {dir_color}; font-size: 1.1rem; font-weight: 700;">
            {next_candle["target_price"]:,.2f}
        </span>
        <span style="color: #8b949e; font-size: 0.8rem;"> 
            ({dir_arrow} {abs(next_candle["target_price"] - next_candle["current_price"]):.2f} points)
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ROW 2: AI PREDICTION + CHART ──────────────────────────────────────────
    col_pred, col_chart = st.columns([1, 2.5])

    with col_pred:
        direction = prediction.get("direction", "SIDEWAYS")
        strength = prediction.get("strength", "WEAK")
        consensus = prediction.get("consensus", "UNKNOWN")
        agreement = prediction.get("agreement", "UNKNOWN")
        
        pred_class = {"BULLISH": "prediction-bullish", "BEARISH": "prediction-bearish"}.get(direction, "prediction-sideways")
        pred_color_class = {"BULLISH": "pred-bull", "BEARISH": "pred-bear"}.get(direction, "pred-side")
        pred_emoji = {"BULLISH": "🚀", "BEARISH": "📉"}.get(direction, "↔")
        
        # Consensus badge
        consensus_badge = ""
        if consensus == "STRONG":
            consensus_badge = '<span style="background:#0d2818;border:1px solid #3fb950;color:#3fb950;padding:2px 8px;border-radius:12px;font-size:0.65rem;font-weight:700;">✓✓ STRONG CONSENSUS</span>'
        elif consensus == "MODERATE":
            consensus_badge = '<span style="background:#2d2100;border:1px solid #d29922;color:#d29922;padding:2px 8px;border-radius:12px;font-size:0.65rem;font-weight:700;">✓ MODERATE CONSENSUS</span>'
        elif consensus == "WEAK":
            consensus_badge = '<span style="background:#2d0f0f;border:1px solid #f85149;color:#f85149;padding:2px 8px;border-radius:12px;font-size:0.65rem;font-weight:700;">⚠ CONFLICTING</span>'
        elif consensus in ["GROQ_ONLY", "GEMINI_ONLY"]:
            consensus_badge = '<span style="background:#1c2128;border:1px solid #58a6ff;color:#58a6ff;padding:2px 8px;border-radius:12px;font-size:0.65rem;font-weight:700;">SINGLE AI</span>'

        st.markdown(f"""
        <div class="prediction-card {pred_class}">
            <div class="metric-label">🤖 DUAL-AI PREDICTION — NEXT 5–40 MINS</div>
            <div class="pred-direction {pred_color_class}">{pred_emoji} {direction}</div>
            <div style="font-size:0.8rem;color:#8b949e;margin:4px 0;">
                Strength: <b style="color:#f0f6fc;">{strength}</b> | 
                Confidence: <b style="color:{conf_color};">{confidence}%</b>
            </div>
            <div style="margin:6px 0;">{consensus_badge}</div>
            <div class="confidence-bar-container">
                <div class="confidence-bar" style="width:{confidence}%;background:{conf_color};"></div>
            </div>
            <div style="font-size:0.8rem;color:#c9d1d9;margin-top:10px;font-style:italic;">
                "{prediction.get('one_line_summary', 'Analyzing...')}"
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show individual AI predictions if available
        groq_pred = prediction.get("groq_prediction", {})
        gemini_pred = prediction.get("gemini_prediction", {})
        
        if groq_pred and gemini_pred and not groq_pred.get("error") and not gemini_pred.get("error"):
            groq_dir = prediction.get("groq_direction", "N/A")
            gemini_dir = prediction.get("gemini_direction", "N/A")
            groq_conf = prediction.get("groq_confidence", 0)
            gemini_conf = prediction.get("gemini_confidence", 0)
            
            # Color code based on agreement
            if groq_dir == gemini_dir:
                groq_color = gemini_color = "#3fb950"
            elif agreement == "PARTIAL":
                groq_color = gemini_color = "#d29922"
            else:
                groq_color = "#f85149" if groq_dir == "BEARISH" else "#3fb950" if groq_dir == "BULLISH" else "#d29922"
                gemini_color = "#f85149" if gemini_dir == "BEARISH" else "#3fb950" if gemini_dir == "BULLISH" else "#d29922"
            
            st.markdown(f"""
            <div style="background:#161b22;border:1px solid #21262d;border-radius:8px;padding:8px;margin-top:8px;">
                <div style="font-size:0.65rem;color:#8b949e;margin-bottom:6px;text-transform:uppercase;letter-spacing:0.5px;">Individual AI Predictions</div>
                <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                    <span style="font-size:0.72rem;color:#8b949e;">Groq (Llama 3.3 70B):</span>
                    <span style="font-size:0.72rem;color:{groq_color};font-weight:700;">{groq_dir} ({groq_conf}%)</span>
                </div>
                <div style="display:flex;justify-content:space-between;">
                    <span style="font-size:0.72rem;color:#8b949e;">Gemini (1.5 Flash):</span>
                    <span style="font-size:0.72rem;color:{gemini_color};font-weight:700;">{gemini_dir} ({gemini_conf}%)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Price Targets
        targets = prediction.get("price_targets", {})
        if targets:
            st.markdown('<div class="section-header">PRICE TARGETS</div>', unsafe_allow_html=True)
            for horizon, vals in targets.items():
                if isinstance(vals, dict):
                    st.markdown(f"""
                    <div class="metric-card" style="margin-bottom:6px;">
                        <div class="metric-label">+{horizon}</div>
                        <div style="font-size:0.8rem;color:#f0f6fc;">
                            H: <span style="color:#3fb950;">{vals.get('high','?'):,}</span> &nbsp;
                            L: <span style="color:#f85149;">{vals.get('low','?'):,}</span> &nbsp;
                            Target: <span style="color:#58a6ff;font-weight:700;">{vals.get('most_likely','?'):,}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # Key Levels
        key_levels = prediction.get("key_levels", {})
        if key_levels:
            st.markdown('<div class="section-header" style="margin-top:10px;">KEY LEVELS</div>', unsafe_allow_html=True)
            for k, v in key_levels.items():
                label = k.replace("_", " ").title()
                color = "#f85149" if "resist" in k else "#3fb950"
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #21262d;font-size:0.78rem;">
                    <span style="color:#8b949e;">{label}</span>
                    <span style="color:{color};font-family:'Space Mono',monospace;font-weight:600;">{v:,}</span>
                </div>
                """, unsafe_allow_html=True)

        # Top Reasons
        reasons = prediction.get("top_3_reasons", [])
        if reasons:
            st.markdown('<div class="section-header" style="margin-top:10px;">WHY</div>', unsafe_allow_html=True)
            for i, r in enumerate(reasons, 1):
                st.markdown(f'<div style="font-size:0.75rem;color:#c9d1d9;padding:3px 0;">{i}. {r}</div>', unsafe_allow_html=True)

        # Options Strategy
        strategy = prediction.get("options_strategy", {})
        if strategy:
            risk = strategy.get("risk", "MEDIUM")
            risk_color = "#3fb950" if risk == "LOW" else "#f85149" if risk == "HIGH" else "#d29922"
            st.markdown(f"""
            <div class="metric-card" style="margin-top:10px;">
                <div class="metric-label">SUGGESTED STRATEGY</div>
                <div style="font-size:0.9rem;font-weight:700;color:#58a6ff;">{strategy.get('recommended','N/A')}</div>
                <div style="font-size:0.72rem;color:#8b949e;margin-top:3px;">{strategy.get('strikes','')}</div>
                <div style="font-size:0.72rem;color:#c9d1d9;margin-top:3px;">{strategy.get('rationale','')}</div>
                <div style="margin-top:4px;font-size:0.68rem;">Risk: <span style="color:{risk_color};font-weight:700;">{risk}</span></div>
            </div>
            """, unsafe_allow_html=True)

        # Do Not Trade Warning
        dnt = prediction.get("do_not_trade_if", "")
        if dnt:
            st.markdown(f"""
            <div style="background:#2d1a00;border:1px solid #d29922;border-radius:8px;padding:0.6rem;margin-top:8px;">
                <div style="font-size:0.68rem;color:#d29922;font-weight:700;">⚠️ DO NOT TRADE IF</div>
                <div style="font-size:0.72rem;color:#c9d1d9;margin-top:3px;">{dnt}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_chart:
        # Candlestick Chart with Indicators
        if not df_candles.empty:
            # Only show today's candles
            today = datetime.now(IST).date()
            df_today = df_candles[df_candles.index.date == today]
            if df_today.empty:
                df_today = df_candles.tail(78)  # ~6.5hr * 12 5min candles

            fig = make_subplots(
                rows=3, cols=1,
                row_heights=[0.6, 0.2, 0.2],
                vertical_spacing=0.03,
                shared_xaxes=True,
            )

            # Candlestick
            fig.add_trace(go.Candlestick(
                x=df_today.index,
                open=df_today["open"], high=df_today["high"],
                low=df_today["low"], close=df_today["close"],
                name="NIFTY",
                increasing=dict(line=dict(color="#3fb950"), fillcolor="#0d2818"),
                decreasing=dict(line=dict(color="#f85149"), fillcolor="#2d0f0f"),
            ), row=1, col=1)

            # EMAs
            colors_ema = {"ema9": "#ffa726", "ema21": "#42a5f5", "ema50": "#ab47bc"}
            for col_name, color in colors_ema.items():
                if col_name in df_today:
                    fig.add_trace(go.Scatter(
                        x=df_today.index, y=df_today[col_name],
                        mode="lines", name=col_name.upper(),
                        line=dict(color=color, width=1.2),
                    ), row=1, col=1)

            # VWAP
            if "vwap" in df_today:
                fig.add_trace(go.Scatter(
                    x=df_today.index, y=df_today["vwap"],
                    mode="lines", name="VWAP",
                    line=dict(color="#ffffff", width=1.2, dash="dot"),
                ), row=1, col=1)

            # BB
            if "bb_upper" in df_today:
                fig.add_trace(go.Scatter(x=df_today.index, y=df_today["bb_upper"],
                    mode="lines", name="BB Upper", line=dict(color="#58a6ff", width=0.8, dash="dash"), showlegend=False), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_today.index, y=df_today["bb_lower"],
                    mode="lines", name="BB Lower", line=dict(color="#58a6ff", width=0.8, dash="dash"), showlegend=False,
                    fill="tonexty", fillcolor="rgba(88,166,255,0.05)"), row=1, col=1)

            # Key OI Levels
            if oi_data.get("support"):
                fig.add_hline(y=oi_data["support"], line_dash="dash", line_color="#3fb950",
                              line_width=1, annotation_text=f"Support {oi_data['support']:,.0f}", row=1, col=1)
            if oi_data.get("resistance"):
                fig.add_hline(y=oi_data["resistance"], line_dash="dash", line_color="#f85149",
                              line_width=1, annotation_text=f"Resistance {oi_data['resistance']:,.0f}", row=1, col=1)
            if oi_data.get("max_pain"):
                fig.add_hline(y=oi_data["max_pain"], line_dash="dot", line_color="#d29922",
                              line_width=1.5, annotation_text=f"Max Pain {oi_data['max_pain']:,.0f}", row=1, col=1)

            # RSI
            if "rsi" in df_today:
                fig.add_trace(go.Scatter(
                    x=df_today.index, y=df_today["rsi"],
                    mode="lines", name="RSI",
                    line=dict(color="#ab47bc", width=1.5),
                ), row=2, col=1)
                fig.add_hline(y=70, line_color="#f85149", line_width=0.8, line_dash="dot", row=2, col=1)
                fig.add_hline(y=30, line_color="#3fb950", line_width=0.8, line_dash="dot", row=2, col=1)

            # MACD
            if "macd" in df_today:
                fig.add_trace(go.Scatter(x=df_today.index, y=df_today["macd"],
                    mode="lines", name="MACD", line=dict(color="#42a5f5", width=1.2)), row=3, col=1)
                fig.add_trace(go.Scatter(x=df_today.index, y=df_today["macd_signal"],
                    mode="lines", name="Signal", line=dict(color="#ffa726", width=1.2)), row=3, col=1)
                colors_hist = ["#3fb950" if v >= 0 else "#f85149" for v in df_today["macd_hist"]]
                fig.add_trace(go.Bar(x=df_today.index, y=df_today["macd_hist"],
                    name="Histogram", marker_color=colors_hist, showlegend=False), row=3, col=1)

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0a0a0f",
                plot_bgcolor="#0d1117",
                height=580,
                margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(orientation="h", y=1.02, x=0, font=dict(size=10), bgcolor="rgba(0,0,0,0)"),
                xaxis_rangeslider_visible=False,
                font=dict(family="Space Mono", color="#8b949e", size=10),
            )
            fig.update_xaxes(gridcolor="#21262d", showgrid=True)
            fig.update_yaxes(gridcolor="#21262d", showgrid=True)

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Chart data unavailable. Market may be closed or data source unreachable.")

    # ── ROW 3: OI CHART + INDICATORS + NEWS ──────────────────────────────────
    col_oi, col_ind, col_news = st.columns([1.2, 1, 1])

    with col_oi:
        st.markdown('<div class="section-header">📊 OPEN INTEREST ANALYSIS</div>', unsafe_allow_html=True)
        chain = oi_data.get("chain", pd.DataFrame())
        if not chain.empty and price > 0:
            # Show strikes near current price (±1000 pts)
            near = chain[(chain["strike"] >= price - 1000) & (chain["strike"] <= price + 1000)]
            if not near.empty:
                fig_oi = go.Figure()
                fig_oi.add_trace(go.Bar(
                    x=near["ce_oi"], y=near["strike"],
                    orientation="h", name="CE OI",
                    marker_color="#f85149", opacity=0.8,
                ))
                fig_oi.add_trace(go.Bar(
                    x=[-v for v in near["pe_oi"]], y=near["strike"],
                    orientation="h", name="PE OI",
                    marker_color="#3fb950", opacity=0.8,
                ))
                fig_oi.add_hline(y=price, line_color="#ffffff", line_width=1.5, line_dash="solid",
                                 annotation_text="Current", annotation_position="right")
                if oi_data.get("max_pain"):
                    fig_oi.add_hline(y=oi_data["max_pain"], line_color="#d29922",
                                     line_width=1, line_dash="dash",
                                     annotation_text="Max Pain", annotation_position="right")
                fig_oi.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="#0a0a0f",
                    plot_bgcolor="#0d1117",
                    height=360,
                    barmode="overlay",
                    margin=dict(l=5, r=5, t=5, b=5),
                    legend=dict(orientation="h", y=1.02, font=dict(size=9)),
                    yaxis=dict(title="Strike", gridcolor="#21262d"),
                    xaxis=dict(title="OI (Left=PE, Right=CE)", gridcolor="#21262d"),
                    font=dict(family="Space Mono", color="#8b949e", size=9),
                )
                st.plotly_chart(fig_oi, use_container_width=True)

                # OI Stats
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">🛡 Support (PE OI)</div>
                        <div class="metric-value" style="color:#3fb950;">{oi_data.get('support', 'N/A'):,}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_b:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">🧱 Resistance (CE OI)</div>
                        <div class="metric-value" style="color:#f85149;">{oi_data.get('resistance', 'N/A'):,}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("OI data unavailable. Fetching from Angel One...")

    with col_ind:
        st.markdown('<div class="section-header">📡 TECHNICAL SIGNALS</div>', unsafe_allow_html=True)

        if indicator_summary:
            for ind_name, data in indicator_summary.items():
                signal = data.get("signal", "NEUTRAL")
                val = data.get("value", "")
                display_name = ind_name.replace("_", " ")
                badge = signal_badge(signal)
                val_str = f"{val:,.2f}" if isinstance(val, (int, float)) else str(val)
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;
                            padding:5px 0;border-bottom:1px solid #21262d;">
                    <div>
                        <div style="font-size:0.75rem;color:#8b949e;">{display_name}</div>
                        <div style="font-size:0.7rem;color:#c9d1d9;">{val_str}</div>
                    </div>
                    {badge}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Loading indicators...")

        # Candlestick Patterns
        if patterns:
            st.markdown('<div class="section-header" style="margin-top:12px;">🕯 PATTERNS DETECTED</div>', unsafe_allow_html=True)
            for pattern, meaning in patterns.items():
                is_bull = any(x in pattern.lower() for x in ["bull", "hammer"])
                color = "#3fb950" if is_bull else "#f85149"
                st.markdown(f"""
                <div style="background:#161b22;border:1px solid {color}33;border-left:3px solid {color};
                            border-radius:6px;padding:5px 8px;margin-bottom:4px;">
                    <div style="font-size:0.75rem;color:{color};font-weight:600;">{pattern}</div>
                    <div style="font-size:0.68rem;color:#8b949e;">{meaning}</div>
                </div>
                """, unsafe_allow_html=True)

        # Greeks Summary
        if greeks:
            st.markdown('<div class="section-header" style="margin-top:12px;">🔢 ATM GREEKS</div>', unsafe_allow_html=True)
            interp = greeks.get("interpretation", {})
            ce_g = greeks.get("CE", {})
            pe_g = greeks.get("PE", {})
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:0.72rem;color:#8b949e;">Strike: <b style="color:#f0f6fc;">{greeks.get('strike',0):,}</b> | DTE: <b style="color:#f0f6fc;">{greeks.get('days_to_expiry',0):.1f}d</b></div>
                <div style="font-size:0.72rem;margin-top:4px;">
                    CE Δ <span style="color:#3fb950;">{ce_g.get('delta',0):.3f}</span> &nbsp;
                    PE Δ <span style="color:#f85149;">{pe_g.get('delta',0):.3f}</span>
                </div>
                <div style="font-size:0.72rem;">
                    Θ/day: <span style="color:#d29922;">{abs(ce_g.get('theta',0)):.2f}</span> &nbsp;
                    Vega: <span style="color:#58a6ff;">{ce_g.get('vega',0):.2f}</span>
                </div>
                <div style="font-size:0.68rem;color:#d29922;margin-top:4px;">{interp.get('expiry_warning','')}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_news:
        st.markdown('<div class="section-header">📰 NEWS SENTIMENT</div>', unsafe_allow_html=True)

        news_sent = news_data.get("sentiment", {})
        overall = news_sent.get("overall", "NEUTRAL")
        news_score = news_sent.get("score", 0)
        bull_c = news_sent.get("bullish_count", 0)
        bear_c = news_sent.get("bearish_count", 0)
        total_c = news_sent.get("total_articles", 0)

        sent_color = "#3fb950" if overall == "BULLISH" else "#f85149" if overall == "BEARISH" else "#d29922"
        st.markdown(f"""
        <div class="metric-card" style="margin-bottom:10px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div class="metric-label">Overall Sentiment</div>
                    <div class="metric-value" style="color:{sent_color};">{overall}</div>
                </div>
                <div style="text-align:right;font-size:0.72rem;color:#8b949e;">
                    🐂 {bull_c} | 🐻 {bear_c}<br>
                    {total_c} articles
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        articles = news_data.get("articles", [])
        if articles:
            for article in articles[:8]:
                sent = article.get("sentiment", {})
                s_label = sent.get("label", "NEUTRAL")
                s_color = "#3fb950" if s_label == "BULLISH" else "#f85149" if s_label == "BEARISH" else "#8b949e"
                hi = "⚡" if sent.get("high_impact") else ""
                st.markdown(f"""
                <div class="news-item">
                    <div class="news-title">{hi}{article.get('title','')[:90]}{'...' if len(article.get('title','')) > 90 else ''}</div>
                    <div class="news-meta">
                        {article.get('source','?')} · {article.get('published','?')} &nbsp;
                        <span style="color:{s_color};font-weight:600;">{s_label}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Fetching news feeds...")

    # ── ROW 4: GLOBAL CUES ────────────────────────────────────────────────────
    st.markdown('<div class="section-header" style="margin-top:8px;">🌍 GLOBAL CUES</div>', unsafe_allow_html=True)
    cols_global = st.columns(len(global_cues) if global_cues else 7)
    for i, (name, data) in enumerate(global_cues.items()):
        if i < len(cols_global):
            with cols_global[i]:
                val = data.get("pct_change", 0)
                price = data.get("price", 0)
                color = "#3fb950" if val >= 0 else "#f85149"
                arrow = "▲" if val >= 0 else "▼"
                
                # Format price based on market type
                if "USD/INR" in name or "INR" in name:
                    price_str = f"₹{price:,.2f}"
                elif "Gold" in name or "Crude" in name:
                    price_str = f"${price:,.2f}"
                else:
                    price_str = f"${price:,.0f}"
                
                st.markdown(f"""
                <div class="metric-card" style="padding:0.5rem;">
                    <div class="metric-label" style="font-size:0.68rem;">{name}</div>
                    <div style="font-size:0.85rem;color:{color};font-weight:700;font-family:'Space Mono',monospace;">
                        {arrow} {abs(val):.2f}%
                    </div>
                    <div style="font-size:0.65rem;color:#8b949e;margin-top:2px;">
                        {price_str}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # ── ROW 5: VOLATILITY FORECASTING ─────────────────────────────────────────
    st.markdown('<div class="section-header" style="margin-top:16px;">📊 VOLATILITY FORECAST</div>', unsafe_allow_html=True)
    
    # Get volatility forecast
    vol_forecast = None
    if not df_candles.empty:
        try:
            vol_forecast = get_volatility_forecast(df_candles, vix_data.get('vix'))
        except Exception as e:
            logger.error(f"Error getting volatility forecast: {e}")
    
    if vol_forecast and 'error' not in vol_forecast:
        col_vol_current, col_vol_forecast, col_vol_implications = st.columns([1, 1.5, 1.5])
        
        with col_vol_current:
            st.markdown("#### Current Volatility")
            
            current_vol = vol_forecast.get('current_volatility', {})
            ensemble = current_vol.get('ensemble', 0)
            regime = vol_forecast.get('regime', {})
            trend = vol_forecast.get('trend', {})
            
            # Regime color
            regime_name = regime.get('regime', 'UNKNOWN')
            if 'LOW' in regime_name:
                regime_color = theme['green']
            elif 'HIGH' in regime_name or 'EXTREME' in regime_name:
                regime_color = theme['red']
            elif 'ELEVATED' in regime_name:
                regime_color = theme['yellow']
            else:
                regime_color = theme['accent']
            
            # Trend color
            trend_name = trend.get('trend', 'UNKNOWN')
            if 'INCREASING' in trend_name:
                trend_color = theme['red']
            elif 'DECREASING' in trend_name:
                trend_color = theme['green']
            else:
                trend_color = theme['text_muted']
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Ensemble Volatility</div>
                <div class="metric-value" style="color:{regime_color}">{ensemble:.2f}%</div>
                <div style="font-size:0.75rem;color:{regime_color};margin-top:4px;">
                    {regime_name}
                </div>
                <div style="font-size:0.68rem;color:{theme['text_muted']};margin-top:6px;">
                    {regime.get('description', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card" style="margin-top:8px;">
                <div class="metric-label">Volatility Trend</div>
                <div style="font-size:0.9rem;color:{trend_color};font-weight:700;">
                    {trend_name}
                </div>
                <div style="font-size:0.72rem;color:{theme['text_muted']};margin-top:4px;">
                    Change: {trend.get('change_pct', 0):.2f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # VIX comparison if available
            vix_analysis = vol_forecast.get('vix_analysis')
            if vix_analysis:
                hv_vs_vix = vix_analysis.get('hv_vs_vix', 0)
                vix_color = theme['green'] if hv_vs_vix > 0 else theme['red']
                
                st.markdown(f"""
                <div class="metric-card" style="margin-top:8px;">
                    <div class="metric-label">HV vs VIX</div>
                    <div style="font-size:0.85rem;color:{vix_color};font-weight:700;">
                        {hv_vs_vix:+.2f}%
                    </div>
                    <div style="font-size:0.68rem;color:{theme['text_muted']};margin-top:4px;">
                        {vix_analysis.get('interpretation', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col_vol_forecast:
            st.markdown("#### Volatility Forecasts")
            
            forecasts = vol_forecast.get('forecasts', {})
            
            for timeframe in ['5min', '15min', '30min', '1day']:
                if timeframe in forecasts:
                    fc = forecasts[timeframe]
                    forecast_val = fc.get('forecast', 0)
                    range_low = fc.get('range_low', 0)
                    range_high = fc.get('range_high', 0)
                    confidence = fc.get('confidence', 'MEDIUM')
                    
                    # Confidence color
                    conf_color = theme['green'] if confidence == 'HIGH' else theme['yellow'] if confidence == 'MEDIUM' else theme['red']
                    
                    # Timeframe label
                    tf_label = timeframe.replace('min', ' min').replace('day', ' day')
                    
                    st.markdown(f"""
                    <div class="metric-card" style="margin-bottom:8px;">
                        <div class="metric-label">{tf_label.upper()} FORECAST</div>
                        <div style="font-size:1.1rem;color:{theme['accent']};font-weight:700;">
                            {forecast_val:.2f}%
                        </div>
                        <div style="font-size:0.7rem;color:{theme['text_muted']};margin-top:4px;">
                            Range: {range_low:.2f}% - {range_high:.2f}%
                        </div>
                        <div style="font-size:0.68rem;color:{conf_color};margin-top:4px;">
                            Confidence: {confidence}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col_vol_implications:
            st.markdown("#### Trading Implications")
            
            implications = vol_forecast.get('implications', {})
            
            # Options strategy
            options_strat = implications.get('options_strategy', 'N/A')
            position_sizing = implications.get('position_sizing', 'N/A')
            risk_level = implications.get('risk_level', 'MEDIUM')
            
            # Risk level color
            risk_color = theme['green'] if risk_level == 'LOW' else theme['red'] if risk_level == 'HIGH' else theme['yellow']
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Options Strategy</div>
                <div style="font-size:0.85rem;color:{theme['text_primary']};margin-top:4px;line-height:1.4;">
                    {options_strat}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card" style="margin-top:8px;">
                <div class="metric-label">Position Sizing</div>
                <div style="font-size:0.85rem;color:{theme['text_primary']};margin-top:4px;">
                    {position_sizing}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card" style="margin-top:8px;">
                <div class="metric-label">Risk Level</div>
                <div style="font-size:1rem;color:{risk_color};font-weight:700;margin-top:4px;">
                    {risk_level}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Recommendations
            recommendations = implications.get('recommendations', [])
            if recommendations:
                st.markdown(f"""
                <div class="metric-card" style="margin-top:8px;">
                    <div class="metric-label">Recommendations</div>
                    <div style="font-size:0.72rem;color:{theme['text_secondary']};margin-top:6px;line-height:1.6;">
                        {'<br>'.join(['• ' + rec for rec in recommendations])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Volatility forecasting requires sufficient historical data. Please wait for data to load.")

    # ── FOOTER ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center;padding:1rem;margin-top:1rem;
                border-top:1px solid {theme['border']};font-size:0.65rem;color:{theme['text_muted']};">
        ⚠️ This dashboard is for educational & informational purposes only. Not financial advice. 
        Trade at your own risk. | Data: NSE + yfinance + RSS | AI: {prediction.get('model_used','Groq Llama')} | 
        Last AI analysis: {prediction.get('generated_at','N/A')}
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    # Import rate limits for display
    from api_rate_monitor import RATE_LIMITS
    
    # ── SIDEBAR: PRICE ALERTS ─────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🔔 Price Alerts")
        st.markdown("Get notified when Nifty reaches your target price")
        
        # Alert summary
        summary = get_alert_summary()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Active", summary['active'])
        with col2:
            st.metric("Triggered", summary['triggered'])
        
        st.markdown("---")
        
        # Add new alert
        st.markdown("#### Add New Alert")
        
        with st.form("add_alert_form", clear_on_submit=True):
            alert_price = st.number_input(
                "Target Price",
                min_value=10000.0,
                max_value=50000.0,
                value=25500.0,
                step=50.0,
                help="Set the price level for the alert"
            )
            
            alert_direction = st.selectbox(
                "Alert When",
                options=["above", "below"],
                format_func=lambda x: f"Price goes {x} target",
                help="Choose when to trigger the alert"
            )
            
            alert_note = st.text_input(
                "Note (optional)",
                placeholder="e.g., Resistance level",
                help="Add a note to remember why you set this alert"
            )
            
            submitted = st.form_submit_button("➕ Add Alert", use_container_width=True)
            
            if submitted:
                add_alert(alert_price, alert_direction, alert_note)
                st.success(f"✅ Alert added: {alert_direction} {alert_price:,.0f}")
                st.rerun()
        
        st.markdown("---")
        
        # Show active alerts
        active_alerts = get_active_alerts()
        if active_alerts:
            st.markdown("#### Active Alerts")
            for alert in active_alerts:
                direction_emoji = "⬆️" if alert['direction'] == 'above' else "⬇️"
                direction_text = "Above" if alert['direction'] == 'above' else "Below"
                
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"{direction_emoji} **{direction_text} {alert['price']:,.0f}**")
                        if alert['note']:
                            st.caption(alert['note'])
                    with col2:
                        if st.button("🗑️", key=f"del_{alert['id']}", help="Delete alert"):
                            remove_alert(alert['id'])
                            st.rerun()
                    st.markdown("---")
        else:
            st.info("No active alerts. Add one above!")
        
        # Show triggered alerts
        triggered_alerts = get_triggered_alerts()
        if triggered_alerts:
            st.markdown("#### Recently Triggered")
            for alert in triggered_alerts[-3:]:  # Show last 3
                direction_emoji = "⬆️" if alert['direction'] == 'above' else "⬇️"
                triggered_time = datetime.fromisoformat(alert['triggered_at']).strftime('%H:%M:%S')
                st.success(f"{direction_emoji} {alert['price']:,.0f} at {triggered_time}")
            
            if st.button("🗑️ Clear Triggered", use_container_width=True):
                clear_triggered_alerts()
                st.rerun()
        
        # ── API RATE LIMIT MONITORING ─────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 📊 API Usage Monitor")
        st.markdown("Real-time API usage tracking")
        
        # Get usage summary
        summary = get_usage_summary()
        
        # Show overall status
        if summary['all_ok']:
            st.success(f"✅ All APIs OK - {summary['total_calls_today']:,} calls today")
        elif summary['critical_count'] > 0:
            st.error(f"🚨 {summary['critical_count']} API(s) at critical usage!")
        elif summary['warning_count'] > 0:
            st.warning(f"⚠️ {summary['warning_count']} API(s) approaching limits")
        
        # Show alerts if any
        alerts = check_rate_limit_alerts()
        if alerts:
            for alert in alerts:
                if alert['level'] == 'CRITICAL':
                    st.error(f"🚨 {alert['message']}")
                else:
                    st.warning(f"⚠️ {alert['message']}")
        
        # Show detailed stats in expander
        with st.expander("📈 Detailed Usage Stats", expanded=False):
            all_stats = get_all_usage_stats()
            
            for api_name, stats in all_stats.items():
                if not stats:
                    continue
                
                # Status emoji
                if stats['status'] == 'CRITICAL':
                    status_emoji = "🔴"
                elif stats['status'] == 'WARNING':
                    status_emoji = "🟡"
                else:
                    status_emoji = "🟢"
                
                st.markdown(f"**{status_emoji} {stats['display_name']}**")
                
                # Daily usage
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        "Today",
                        f"{stats['daily_calls']:,}",
                        f"{stats['daily_pct']:.1f}%"
                    )
                with col2:
                    st.metric(
                        "Limit",
                        f"{stats['daily_limit']:,}",
                        f"{stats['remaining_daily']:,} left"
                    )
                
                # Progress bar
                progress_color = stats['color']
                st.progress(
                    min(stats['daily_pct'] / 100, 1.0),
                    text=f"{stats['daily_calls']:,} / {stats['daily_limit']:,}"
                )
                
                st.markdown("---")
        
        # Show estimated end-of-day usage
        with st.expander("🔮 Estimated Daily Usage", expanded=False):
            try:
                estimated = get_estimated_daily_usage()
                
                if estimated and isinstance(estimated, dict):
                    st.markdown("Based on current usage rate:")
                    
                    for api, est in estimated.items():
                        if isinstance(est, dict) and 'estimated_pct' in est:
                            if est['estimated_pct'] >= 95:
                                status = "🔴 CRITICAL"
                            elif est['estimated_pct'] >= 80:
                                status = "🟡 WARNING"
                            else:
                                status = "🟢 OK"
                            
                            st.markdown(f"**{RATE_LIMITS[api]['name']}** {status}")
                            st.markdown(
                                f"Current: {est['current']:,} → "
                                f"Estimated: {est['estimated']:,} / {est['limit']:,} "
                                f"({est['estimated_pct']:.1f}%)"
                            )
                            st.markdown("---")
                else:
                    st.info("No estimation data available yet")
            except Exception as e:
                st.info("Estimation data will be available after some API usage")
        
        # ── BACKTESTING ENGINE ────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 📊 Backtesting Engine")
        st.markdown("Test AI predictions on historical data")
        
        if st.button("🚀 Open Backtesting", use_container_width=True, type="primary"):
            st.session_state.show_backtest = True
        
        if st.session_state.get('show_backtest', False):
            st.info("💡 Backtesting UI will open in a new section below")
    
    # ── BACKTESTING UI (if enabled) ───────────────────────────────────────────
    if st.session_state.get('show_backtest', False):
        st.markdown("---")
        from backtest_ui import render_backtest_ui
        render_backtest_ui()
        
        # Close button
        if st.button("✖ Close Backtesting", type="secondary"):
            st.session_state.show_backtest = False
            st.rerun()
    
    main()
