"""
app.py — Nifty AI Prediction Dashboard (REDESIGNED)
Alt-tab friendly layout - Trade signals first, everything else in tabs
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
from data_fetcher import get_live_nifty_price, get_candle_data, get_india_vix, get_options_chain, get_global_cues, get_market_status
from indicators import calculate_all_indicators, get_indicator_summary
from news_fetcher_scheduled import get_all_news
from ai_engine_consensus import get_rule_based_prediction
from enhanced_prediction_engine import get_enhanced_prediction, initialize_previous_day_levels
from prediction_logger import log_prediction
from price_alerts import add_alert, remove_alert, get_active_alerts, check_alerts, clear_triggered_alerts

IST = pytz.timezone("Asia/Kolkata")

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nifty Trader",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── THEME SYSTEM ─────────────────────────────────────────────────────────────
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

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
}}

.main .block-container {{
    padding: 0.5rem 1rem;
    max-width: 100%;
}}

/* MASSIVE TRADE SIGNAL ALERT */
.signal-alert {{
    border-radius: 16px;
    padding: 32px;
    margin-bottom: 16px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    animation: pulse 2s ease-in-out infinite;
}}

@keyframes pulse {{
    0%, 100% {{ transform: scale(1); }}
    50% {{ transform: scale(1.02); }}
}}

.signal-call {{
    background: linear-gradient(135deg, {theme['green_bg']} 0%, {theme['green_bg_alt']} 100%);
    border: 4px solid {theme['green']};
}}

.signal-put {{
    background: linear-gradient(135deg, {theme['red_bg']} 0%, {theme['red_bg_alt']} 100%);
    border: 4px solid {theme['red']};
}}

.signal-scanning {{
    background: {theme['bg_tertiary']};
    border: 2px solid {theme['border_light']};
}}

.signal-title {{
    font-family: 'Space Mono', monospace;
    font-size: 3.5rem;
    font-weight: 700;
    letter-spacing: 2px;
    margin-bottom: 16px;
}}

.signal-details {{
    font-size: 1.2rem;
    margin-top: 20px;
}}

/* METRIC CARDS */
.metric-card-large {{
    background: {theme['bg_tertiary']};
    border: 1px solid {theme['border']};
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}}

.metric-label-large {{
    font-size: 0.75rem;
    color: {theme['text_muted']};
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 8px;
}}

.metric-value-large {{
    font-family: 'Space Mono', monospace;
    font-size: 2.5rem;
    font-weight: 700;
    color: {theme['text_primary']};
}}

/* INDICATOR SCORES */
.indicator-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    margin: 8px 0;
    background: {theme['bg_tertiary']};
    border-radius: 8px;
    border-left: 4px solid {theme['border']};
}}

.indicator-bullish {{ border-left-color: {theme['green']}; }}
.indicator-bearish {{ border-left-color: {theme['red']}; }}
.indicator-neutral {{ border-left-color: {theme['yellow']}; }}

.indicator-name {{
    font-size: 1rem;
    font-weight: 600;
    color: {theme['text_primary']};
}}

.indicator-value {{
    font-family: 'Space Mono', monospace;
    font-size: 1.1rem;
    font-weight: 700;
}}

/* TABS */
.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
}}

.stTabs [data-baseweb="tab"] {{
    background: {theme['bg_tertiary']};
    border-radius: 8px 8px 0 0;
    padding: 12px 24px;
    font-weight: 600;
}}

.stTabs [aria-selected="true"] {{
    background: {theme['accent']};
    color: white;
}}

/* SIDEBAR */
section[data-testid="stSidebar"] {{
    background: {theme['bg_secondary']};
    border-right: 1px solid {theme['border']};
}}

</style>
""", unsafe_allow_html=True)

# ── CACHED DATA FETCHERS ──────────────────────────────────────────────────────
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

@st.cache_data(ttl=300)
def cached_oi():
    return get_options_chain()

@st.cache_data(ttl=300)
def cached_news():
    return get_all_news()

@st.cache_data(ttl=120)
def cached_global():
    return get_global_cues()


# ── MAIN DASHBOARD ─────────────────────────────────────────────────────────────
def main():
    # Initialize session state
    if 'dashboard_running' not in st.session_state:
        st.session_state.dashboard_running = True
    
    now_ist = datetime.now(IST)
    market_status = get_market_status()

    # Auto-refresh if running
    if st.session_state.dashboard_running:
        st_autorefresh(interval=REFRESH_INTERVAL_SECONDS * 1000, key="auto_refresh")

    # ── HEADER ROW ─────────────────────────────────────────────────────────────
    col_title, col_theme, col_control = st.columns([4, 1, 1])
    
    with col_title:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 16px;">
            <h1 style="margin: 0; font-family: 'Space Mono', monospace; color: {theme['accent']};">
                ⚡ NIFTY TRADER
            </h1>
            <span style="font-size: 0.9rem; color: {theme['text_muted']};">
                {now_ist.strftime('%d %b %Y %H:%M:%S IST')} • {market_status}
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    with col_theme:
        theme_icon = "☀️" if st.session_state.theme == "dark" else "🌙"
        if st.button(f"{theme_icon}", use_container_width=True):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()
    
    with col_control:
        if st.session_state.dashboard_running:
            if st.button("⏸ PAUSE", use_container_width=True):
                st.session_state.dashboard_running = False
                st.rerun()
        else:
            if st.button("▶ START", use_container_width=True):
                st.session_state.dashboard_running = True
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── FETCH ALL DATA ─────────────────────────────────────────────────────────
    with st.spinner(""):
        price_data = cached_price("NIFTY")
        df_candles = cached_candles("NIFTY")
        vix_data = cached_vix()
        oi_data = cached_oi()
        news_data = cached_news()
        global_cues = cached_global()
    
    indicator_summary = get_indicator_summary(df_candles) if not df_candles.empty else {}
    
    if not df_candles.empty:
        initialize_previous_day_levels(df_candles)

    # Check price alerts
    current_price = price_data.get('price', 0)
    if current_price > 0:
        triggered_alerts = check_alerts(current_price)
        if triggered_alerts:
            for alert in triggered_alerts:
                direction_text = "crossed above" if alert['direction'] == 'above' else "dropped below"
                st.toast(f"🔔 PRICE ALERT: Nifty {direction_text} {alert['price']:,.0f}", icon="🔔")

    # ── TRADE SIGNAL SCANNER (SECTION 1 - TOP ALWAYS) ─────────────────────────
    trade_signal = {"signal": "NO_TRADE", "reason": "Not scanned"}
    
    if not df_candles.empty and market_status == "MARKET OPEN":
        from trade_signal_scanner import scan_for_signals
        try:
            trade_signal = scan_for_signals(df_candles)
        except Exception as e:
            trade_signal = {"signal": "NO_TRADE", "reason": f"Scanner error: {str(e)}"}
    
    # Display MASSIVE trade signal alert
    if trade_signal['signal'] == 'BUY':
        st.markdown(f"""
        <div class="signal-alert signal-call">
            <div class="signal-title" style="color: {theme['green']};">
                🟢 CALL SETUP DETECTED
            </div>
            <div class="signal-details">
                <div style="font-size: 1.5rem; margin: 16px 0;">
                    <strong>Entry:</strong> ₹{trade_signal.get('entry', 0):,.2f} &nbsp;|&nbsp;
                    <strong>Stop:</strong> ₹{trade_signal.get('stop_loss', 0):,.2f} &nbsp;|&nbsp;
                    <strong>Target:</strong> ₹{trade_signal.get('target_2', 0):,.2f}
                </div>
                <div style="font-size: 1.2rem; color: {theme['green']};">
                    Risk:Reward 1:{trade_signal.get('risk_reward_ratio', 0):.2f} • 
                    Confluence {trade_signal.get('confluence_score', 0)}/7 • 
                    {trade_signal.get('setup_type', 'UNKNOWN')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    elif trade_signal['signal'] == 'SELL':
        st.markdown(f"""
        <div class="signal-alert signal-put">
            <div class="signal-title" style="color: {theme['red']};">
                🔴 PUT SETUP DETECTED
            </div>
            <div class="signal-details">
                <div style="font-size: 1.5rem; margin: 16px 0;">
                    <strong>Entry:</strong> ₹{trade_signal.get('entry', 0):,.2f} &nbsp;|&nbsp;
                    <strong>Stop:</strong> ₹{trade_signal.get('stop_loss', 0):,.2f} &nbsp;|&nbsp;
                    <strong>Target:</strong> ₹{trade_signal.get('target_2', 0):,.2f}
                </div>
                <div style="font-size: 1.2rem; color: {theme['red']};">
                    Risk:Reward 1:{trade_signal.get('risk_reward_ratio', 0):.2f} • 
                    Confluence {trade_signal.get('confluence_score', 0)}/7 • 
                    {trade_signal.get('setup_type', 'UNKNOWN')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.markdown(f"""
        <div class="signal-alert signal-scanning">
            <div class="signal-title" style="color: {theme['text_muted']}; font-size: 2rem;">
                🔍 SCANNING...
            </div>
            <div style="font-size: 1rem; color: {theme['text_muted']}; margin-top: 8px;">
                No setup detected • {trade_signal.get('reason', 'Waiting for confluence')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── THREE METRIC CARDS (SECTION 1 - BELOW SIGNAL) ─────────────────────────
    col1, col2, col3 = st.columns(3)
    
    with col1:
        price = price_data.get("price", 0)
        change = price_data.get("change", 0)
        pct = price_data.get("pct_change", 0)
        chg_color = theme['green'] if change >= 0 else theme['red']
        chg_arrow = "▲" if change >= 0 else "▼"
        
        st.markdown(f"""
        <div class="metric-card-large">
            <div class="metric-label-large">NIFTY 50</div>
            <div class="metric-value-large">{price:,.2f}</div>
            <div style="font-size: 1.2rem; color: {chg_color}; margin-top: 8px;">
                {chg_arrow} {abs(change):,.2f} ({abs(pct):.2f}%)
            </div>
            <div style="font-size: 0.7rem; color: {theme['text_muted']}; margin-top: 4px;">
                {price_data.get('source', 'N/A')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Get market regime from prediction
        prediction = {}
        try:
            prediction = get_enhanced_prediction(
                price_data, indicator_summary, df_candles,
                oi_data, vix_data, news_data.get("sentiment", {})
            )
        except:
            prediction = {"direction": "UNKNOWN", "confidence": 0, "regime": "UNKNOWN"}
        
        regime = prediction.get("regime", "UNKNOWN")
        # Fallback for empty or None regime
        if not regime or regime == '' or regime is None or regime == "UNKNOWN":
            regime = 'NEUTRAL'
        regime_color = theme['green'] if regime == "TRENDING" else theme['yellow'] if regime == "RANGING" else theme['text_muted']
        
        st.markdown(f"""
        <div class="metric-card-large">
            <div class="metric-label-large">MARKET REGIME</div>
            <div class="metric-value-large" style="color: {regime_color}; font-size: 2rem;">
                {regime}
            </div>
            <div style="font-size: 0.9rem; color: {theme['text_muted']}; margin-top: 8px;">
                ADX-based detection
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        status_color = theme['green'] if "OPEN" in market_status else theme['red']
        status_icon = "🟢" if "OPEN" in market_status else "🔴"
        
        st.markdown(f"""
        <div class="metric-card-large">
            <div class="metric-label-large">MARKET STATUS</div>
            <div class="metric-value-large" style="color: {status_color}; font-size: 2rem;">
                {status_icon} {market_status.split()[1] if len(market_status.split()) > 1 else market_status}
            </div>
            <div style="font-size: 0.9rem; color: {theme['text_muted']}; margin-top: 8px;">
                {now_ist.strftime('%H:%M:%S IST')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── TABS (SECTION 2) ───────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Indicators", 
        "📈 Chart", 
        "📋 Signal Log", 
        "🎯 Model Accuracy", 
        "📰 News"
    ])
    
    # ── TAB 1: INDICATORS ──────────────────────────────────────────────────────
    with tab1:
        st.markdown(f"<h3 style='color: {theme['accent']};'>Technical Indicators</h3>", unsafe_allow_html=True)
        
        # RSI
        rsi_val = indicator_summary.get('RSI', {}).get('value', 50)
        rsi_signal = indicator_summary.get('RSI', {}).get('signal', 'NEUTRAL')
        rsi_class = "indicator-bullish" if "BULL" in rsi_signal else "indicator-bearish" if "BEAR" in rsi_signal else "indicator-neutral"
        rsi_color = theme['green'] if "BULL" in rsi_signal else theme['red'] if "BEAR" in rsi_signal else theme['yellow']
        
        st.markdown(f"""
        <div class="indicator-row {rsi_class}">
            <div class="indicator-name">RSI (14)</div>
            <div class="indicator-value" style="color: {rsi_color};">{rsi_val:.1f} • {rsi_signal}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # MACD
        macd_val = indicator_summary.get('MACD', {}).get('value', 0)
        macd_signal = indicator_summary.get('MACD', {}).get('signal', 'NEUTRAL')
        macd_class = "indicator-bullish" if "BULL" in macd_signal else "indicator-bearish" if "BEAR" in macd_signal else "indicator-neutral"
        macd_color = theme['green'] if "BULL" in macd_signal else theme['red'] if "BEAR" in macd_signal else theme['yellow']
        
        st.markdown(f"""
        <div class="indicator-row {macd_class}">
            <div class="indicator-name">MACD</div>
            <div class="indicator-value" style="color: {macd_color};">{macd_val:.2f} • {macd_signal}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # EMA Trend
        ema_signal = indicator_summary.get('EMA_Trend', {}).get('signal', 'NEUTRAL')
        ema_class = "indicator-bullish" if "BULL" in ema_signal else "indicator-bearish" if "BEAR" in ema_signal else "indicator-neutral"
        ema_color = theme['green'] if "BULL" in ema_signal else theme['red'] if "BEAR" in ema_signal else theme['yellow']
        
        st.markdown(f"""
        <div class="indicator-row {ema_class}">
            <div class="indicator-name">EMA Trend (9/21/50)</div>
            <div class="indicator-value" style="color: {ema_color};">{ema_signal}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Bollinger Bands
        bb_signal = indicator_summary.get('Bollinger_Bands', {}).get('signal', 'NEUTRAL')
        bb_class = "indicator-bullish" if "BULL" in bb_signal else "indicator-bearish" if "BEAR" in bb_signal else "indicator-neutral"
        bb_color = theme['green'] if "BULL" in bb_signal else theme['red'] if "BEAR" in bb_signal else theme['yellow']
        
        st.markdown(f"""
        <div class="indicator-row {bb_class}">
            <div class="indicator-name">Bollinger Bands</div>
            <div class="indicator-value" style="color: {bb_color};">{bb_signal}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # VIX
        vix = vix_data.get("vix", 0)
        vix_signal = "LOW - Sell Premium" if vix < VIX_LOW else "HIGH - Caution" if vix > VIX_HIGH else "NORMAL"
        vix_class = "indicator-bullish" if vix < VIX_LOW else "indicator-bearish" if vix > VIX_HIGH else "indicator-neutral"
        vix_color = theme['green'] if vix < VIX_LOW else theme['red'] if vix > VIX_HIGH else theme['yellow']
        
        st.markdown(f"""
        <div class="indicator-row {vix_class}">
            <div class="indicator-name">India VIX</div>
            <div class="indicator-value" style="color: {vix_color};">{vix:.2f} • {vix_signal}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # ATR
        atr_val = indicator_summary.get('ATR', {}).get('value', 0)
        
        st.markdown(f"""
        <div class="indicator-row indicator-neutral">
            <div class="indicator-name">ATR (14) - Volatility</div>
            <div class="indicator-value" style="color: {theme['text_primary']};">{atr_val:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # PCR (Not implemented yet)
        st.markdown(f"""
        <div class="indicator-row indicator-neutral">
            <div class="indicator-name">PCR (Put/Call Ratio)</div>
            <div class="indicator-value" style="color: {theme['text_muted']};">N/A - Coming Soon</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Max Pain (Not implemented yet)
        st.markdown(f"""
        <div class="indicator-row indicator-neutral">
            <div class="indicator-name">Max Pain</div>
            <div class="indicator-value" style="color: {theme['text_muted']};">N/A - Coming Soon</div>
        </div>
        """, unsafe_allow_html=True)

    # ── TAB 2: CHART ───────────────────────────────────────────────────────────
    with tab2:
        st.markdown(f"<h3 style='color: {theme['accent']};'>Price Chart with Levels</h3>", unsafe_allow_html=True)
        
        if not df_candles.empty:
            today = datetime.now(IST).date()
            df_today = df_candles[df_candles.index.date == today]
            if df_today.empty:
                df_today = df_candles.tail(78)

            fig = make_subplots(
                rows=2, cols=1,
                row_heights=[0.7, 0.3],
                vertical_spacing=0.03,
                shared_xaxes=True,
            )

            # Candlestick
            fig.add_trace(go.Candlestick(
                x=df_today.index,
                open=df_today["Open"], high=df_today["High"],
                low=df_today["Low"], close=df_today["Close"],
                name="NIFTY",
                increasing=dict(line=dict(color=theme['green']), fillcolor=theme['green_bg']),
                decreasing=dict(line=dict(color=theme['red']), fillcolor=theme['red_bg']),
            ), row=1, col=1)

            # EMAs
            colors_ema = {"EMA9": "#ffa726", "EMA21": "#42a5f5", "EMA50": "#ab47bc"}
            for col_name, color in colors_ema.items():
                if col_name in df_today:
                    fig.add_trace(go.Scatter(
                        x=df_today.index, y=df_today[col_name],
                        mode="lines", name=col_name,
                        line=dict(color=color, width=1.5),
                    ), row=1, col=1)

            # Support/Resistance from OI
            if oi_data.get("support"):
                fig.add_hline(y=oi_data["support"], line_dash="dash", line_color=theme['green'],
                              line_width=2, annotation_text=f"Support {oi_data['support']:,.0f}", row=1, col=1)
            if oi_data.get("resistance"):
                fig.add_hline(y=oi_data["resistance"], line_dash="dash", line_color=theme['red'],
                              line_width=2, annotation_text=f"Resistance {oi_data['resistance']:,.0f}", row=1, col=1)
            # Max Pain removed - not implemented yet

            # RSI
            if "RSI" in df_today:
                fig.add_trace(go.Scatter(
                    x=df_today.index, y=df_today["RSI"],
                    mode="lines", name="RSI",
                    line=dict(color="#ab47bc", width=2),
                ), row=2, col=1)
                fig.add_hline(y=70, line_color=theme['red'], line_width=1, line_dash="dot", row=2, col=1)
                fig.add_hline(y=30, line_color=theme['green'], line_width=1, line_dash="dot", row=2, col=1)

            fig.update_layout(
                height=700,
                template="plotly_dark" if st.session_state.theme == "dark" else "plotly_white",
                showlegend=True,
                xaxis_rangeslider_visible=False,
                margin=dict(l=0, r=0, t=0, b=0),
            )
            
            fig.update_yaxes(title_text="Price", row=1, col=1)
            fig.update_yaxes(title_text="RSI", row=2, col=1)

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No candle data available")

    # ── TAB 3: SIGNAL LOG ──────────────────────────────────────────────────────
    with tab3:
        st.markdown(f"<h3 style='color: {theme['accent']};'>Last 20 Trade Signals</h3>", unsafe_allow_html=True)
        
        try:
            # Read prediction log and filter for signals only
            df_log = pd.read_csv('prediction_log.csv')
            
            # Filter for BULLISH or BEARISH predictions (not SIDEWAYS)
            df_signals = df_log[df_log['final_direction'].isin(['BULLISH', 'BEARISH'])].tail(20)
            
            if len(df_signals) > 0:
                # Display as table
                for idx, row in df_signals.iterrows():
                    direction = row['final_direction']
                    confidence = row['confidence']
                    entry_price = row['entry_price']
                    timestamp = pd.to_datetime(row['timestamp']).strftime('%Y-%m-%d %H:%M')
                    outcome = row.get('actual_outcome', None)
                    
                    # Determine outcome text
                    if pd.isna(outcome):
                        outcome_text = "⏳ Pending"
                        outcome_color = theme['text_muted']
                    elif (direction == 'BULLISH' and outcome == 1) or (direction == 'BEARISH' and outcome == -1):
                        outcome_text = "✅ WIN"
                        outcome_color = theme['green']
                    elif (direction == 'BULLISH' and outcome == -1) or (direction == 'BEARISH' and outcome == 1):
                        outcome_text = "❌ LOSS"
                        outcome_color = theme['red']
                    else:
                        outcome_text = "↔ SIDEWAYS"
                        outcome_color = theme['yellow']
                    
                    dir_color = theme['green'] if direction == 'BULLISH' else theme['red']
                    dir_icon = "🟢" if direction == 'BULLISH' else "🔴"
                    
                    st.markdown(f"""
                    <div style="background: {theme['bg_tertiary']}; border-left: 4px solid {dir_color}; 
                                padding: 12px; margin: 8px 0; border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-size: 1.1rem; font-weight: 700; color: {dir_color};">
                                    {dir_icon} {direction}
                                </span>
                                <span style="color: {theme['text_muted']}; margin-left: 12px;">
                                    {timestamp}
                                </span>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-family: 'Space Mono', monospace; font-size: 1rem;">
                                    ₹{entry_price:,.2f}
                                </div>
                                <div style="font-size: 0.85rem; color: {outcome_color}; font-weight: 600;">
                                    {outcome_text}
                                </div>
                            </div>
                        </div>
                        <div style="margin-top: 4px; font-size: 0.85rem; color: {theme['text_muted']};">
                            Confidence: {confidence}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No trade signals logged yet. Signals appear when BULLISH or BEARISH predictions are made.")
                
        except Exception as e:
            st.error(f"❌ Signal log error: {str(e)}")
            st.info("💡 Try running: python scripts/remove_duplicates.py")

    # ── TAB 4: MODEL ACCURACY ──────────────────────────────────────────────────
    with tab4:
        st.markdown(f"<h3 style='color: {theme['accent']};'>Model Performance Tracker</h3>", unsafe_allow_html=True)
        
        try:
            df_log = pd.read_csv('prediction_log.csv')
            
            # Filter for predictions with outcomes
            df_with_outcomes = df_log[df_log['actual_outcome'].notna()]
            
            if len(df_with_outcomes) > 0:
                # Calculate accuracy
                total = len(df_with_outcomes)
                
                # Correct predictions: BULLISH + UP (1), BEARISH + DOWN (-1), SIDEWAYS + SIDEWAYS (0)
                correct = sum([
                    (row['final_direction'] == 'BULLISH' and row['actual_outcome'] == 1) or
                    (row['final_direction'] == 'BEARISH' and row['actual_outcome'] == -1) or
                    (row['final_direction'] == 'SIDEWAYS' and row['actual_outcome'] == 0)
                    for _, row in df_with_outcomes.iterrows()
                ])
                
                accuracy = (correct / total * 100) if total > 0 else 0
                
                # Count by direction
                bullish_total = len(df_with_outcomes[df_with_outcomes['final_direction'] == 'BULLISH'])
                bearish_total = len(df_with_outcomes[df_with_outcomes['final_direction'] == 'BEARISH'])
                sideways_total = len(df_with_outcomes[df_with_outcomes['final_direction'] == 'SIDEWAYS'])
                
                bullish_correct = sum([
                    row['actual_outcome'] == 1
                    for _, row in df_with_outcomes[df_with_outcomes['final_direction'] == 'BULLISH'].iterrows()
                ])
                
                bearish_correct = sum([
                    row['actual_outcome'] == -1
                    for _, row in df_with_outcomes[df_with_outcomes['final_direction'] == 'BEARISH'].iterrows()
                ])
                
                sideways_correct = sum([
                    row['actual_outcome'] == 0
                    for _, row in df_with_outcomes[df_with_outcomes['final_direction'] == 'SIDEWAYS'].iterrows()
                ])
                
                bullish_acc = (bullish_correct / bullish_total * 100) if bullish_total > 0 else 0
                bearish_acc = (bearish_correct / bearish_total * 100) if bearish_total > 0 else 0
                sideways_acc = (sideways_correct / sideways_total * 100) if sideways_total > 0 else 0
                
                # Display overall accuracy
                acc_color = theme['green'] if accuracy >= 60 else theme['yellow'] if accuracy >= 50 else theme['red']
                
                st.markdown(f"""
                <div style="background: {theme['bg_tertiary']}; border: 2px solid {acc_color}; 
                            padding: 24px; border-radius: 12px; text-align: center; margin-bottom: 20px;">
                    <div style="font-size: 0.9rem; color: {theme['text_muted']}; text-transform: uppercase; 
                                letter-spacing: 0.1em; margin-bottom: 8px;">
                        OVERALL ACCURACY
                    </div>
                    <div style="font-family: 'Space Mono', monospace; font-size: 4rem; font-weight: 700; 
                                color: {acc_color};">
                        {accuracy:.1f}%
                    </div>
                    <div style="font-size: 1rem; color: {theme['text_muted']}; margin-top: 8px;">
                        {correct} correct out of {total} predictions
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Display by direction
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div style="background: {theme['green_bg']}; border: 1px solid {theme['green']}; 
                                padding: 16px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 0.8rem; color: {theme['green']}; margin-bottom: 8px;">
                            🟢 BULLISH
                        </div>
                        <div style="font-size: 2rem; font-weight: 700; color: {theme['green']};">
                            {bullish_acc:.1f}%
                        </div>
                        <div style="font-size: 0.8rem; color: {theme['text_muted']}; margin-top: 4px;">
                            {bullish_correct}/{bullish_total}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style="background: {theme['red_bg']}; border: 1px solid {theme['red']}; 
                                padding: 16px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 0.8rem; color: {theme['red']}; margin-bottom: 8px;">
                            🔴 BEARISH
                        </div>
                        <div style="font-size: 2rem; font-weight: 700; color: {theme['red']};">
                            {bearish_acc:.1f}%
                        </div>
                        <div style="font-size: 0.8rem; color: {theme['text_muted']}; margin-top: 4px;">
                            {bearish_correct}/{bearish_total}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div style="background: {theme['yellow_bg']}; border: 1px solid {theme['yellow']}; 
                                padding: 16px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 0.8rem; color: {theme['yellow']}; margin-bottom: 8px;">
                            ↔ SIDEWAYS
                        </div>
                        <div style="font-size: 2rem; font-weight: 700; color: {theme['yellow']};">
                            {sideways_acc:.1f}%
                        </div>
                        <div style="font-size: 0.8rem; color: {theme['text_muted']}; margin-top: 4px;">
                            {sideways_correct}/{sideways_total}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
            else:
                st.info("No predictions with outcomes yet. Outcomes are filled 60 minutes after prediction.")
                
        except Exception as e:
            st.error(f"❌ Model accuracy error: {str(e)}")
            st.info("💡 Try running: python scripts/remove_duplicates.py")

    # ── TAB 5: NEWS ────────────────────────────────────────────────────────────
    with tab5:
        st.markdown(f"<h3 style='color: {theme['accent']};'>Market News & Sentiment</h3>", unsafe_allow_html=True)
        
        if news_data and news_data.get('articles'):
            articles = news_data['articles'][:10]  # Show top 10
            
            for article in articles:
                title = article.get('title', 'No title')
                source = article.get('source', 'Unknown')
                published = article.get('published', 'Unknown')
                link = article.get('link', '#')
                
                st.markdown(f"""
                <div style="background: {theme['bg_tertiary']}; border: 1px solid {theme['border']}; 
                            padding: 12px; margin: 8px 0; border-radius: 8px;">
                    <div style="font-size: 1rem; font-weight: 600; color: {theme['text_primary']}; 
                                margin-bottom: 6px;">
                        <a href="{link}" target="_blank" style="color: {theme['accent']}; text-decoration: none;">
                            {title}
                        </a>
                    </div>
                    <div style="font-size: 0.8rem; color: {theme['text_muted']};">
                        {source} • {published}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No news available")
        
        # Sentiment summary
        sentiment = news_data.get('sentiment', {})
        if sentiment:
            sent_score = sentiment.get('score', None)
            sent_label = sentiment.get('label', 'NEUTRAL')
            sent_color = theme['green'] if sent_label == 'POSITIVE' else theme['red'] if sent_label == 'NEGATIVE' else theme['yellow']
            
            # Format score display
            if sent_score is None or sent_score == 0:
                sent_score_display = 'N/A'
            else:
                sent_score_display = f'{sent_score:.2f}'
            
            st.markdown(f"""
            <div style="background: {theme['bg_tertiary']}; border: 2px solid {sent_color}; 
                        padding: 16px; border-radius: 8px; text-align: center; margin-top: 20px;">
                <div style="font-size: 0.9rem; color: {theme['text_muted']}; margin-bottom: 8px;">
                    NEWS SENTIMENT
                </div>
                <div style="font-size: 2rem; font-weight: 700; color: {sent_color};">
                    {sent_label}
                </div>
                <div style="font-size: 1rem; color: {theme['text_muted']}; margin-top: 4px;">
                    Score: {sent_score_display}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── SIDEBAR: PRICE ALERTS ──────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"<h2 style='color: {theme['accent']};'>🔔 Price Alerts</h2>", unsafe_allow_html=True)
        
        # Add new alert
        with st.expander("➕ Add New Alert", expanded=False):
            alert_price = st.number_input("Price Level", min_value=0.0, value=float(current_price), step=10.0)
            alert_direction = st.selectbox("Direction", ["above", "below"])
            alert_note = st.text_input("Note (optional)")
            
            if st.button("Add Alert", use_container_width=True):
                add_alert(alert_price, alert_direction, alert_note)
                st.success(f"Alert added: {alert_direction} {alert_price:,.0f}")
                st.rerun()
        
        # Show active alerts
        active_alerts = get_active_alerts()
        
        if active_alerts:
            st.markdown(f"<h4 style='color: {theme['text_secondary']};'>Active Alerts ({len(active_alerts)})</h4>", unsafe_allow_html=True)
            
            for alert in active_alerts:
                alert_id = alert['id']
                price = alert['price']
                direction = alert['direction']
                note = alert.get('note', '')
                
                dir_icon = "⬆️" if direction == "above" else "⬇️"
                
                col_alert, col_delete = st.columns([4, 1])
                
                with col_alert:
                    st.markdown(f"""
                    <div style="background: {theme['bg_tertiary']}; padding: 8px; border-radius: 6px; 
                                margin-bottom: 8px;">
                        <div style="font-size: 0.9rem; font-weight: 600;">
                            {dir_icon} {direction.upper()} ₹{price:,.0f}
                        </div>
                        {f'<div style="font-size: 0.75rem; color: {theme["text_muted"]};">{note}</div>' if note else ''}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_delete:
                    if st.button("🗑️", key=f"del_{alert_id}"):
                        remove_alert(alert_id)
                        st.rerun()
        else:
            st.info("No active alerts")
        
        # Clear triggered alerts button
        if st.button("Clear Triggered Alerts", use_container_width=True):
            clear_triggered_alerts()
            st.success("Cleared triggered alerts")
            st.rerun()

    # ── LOG PREDICTION (DISABLED - standalone_logger.py handles all logging) ──
    # Dashboard only READS from CSV, never writes to prevent duplicate rows
    # if prediction and price_data.get("price", 0) > 0 and prediction.get("direction") != "BLOCKED":
    #     try:
    #         last_candle = df_candles.iloc[-1] if not df_candles.empty else {}
    #         
    #         indicator_values = {
    #             'rsi_14': indicator_summary.get('RSI', {}).get('value', 0),
    #             'macd_value': indicator_summary.get('MACD', {}).get('value', 0),
    #             'macd_signal': last_candle.get('MACD_Signal', 0),
    #             'ema_9': indicator_summary.get('EMA_Trend', {}).get('ema_9', 0),
    #             'ema_21': indicator_summary.get('EMA_Trend', {}).get('ema_21', 0),
    #             'ema_50': indicator_summary.get('EMA_Trend', {}).get('ema_50', 0),
    #             'bb_position': (last_candle.get('Close', 0) - last_candle.get('BB_Lower', 0)) / (last_candle.get('BB_Upper', 0) - last_candle.get('BB_Lower', 0)) if (last_candle.get('BB_Upper', 0) - last_candle.get('BB_Lower', 0)) > 0 else 0.5,
    #             'atr_14': indicator_summary.get('ATR', {}).get('value', 0),
    #             'vix': vix_data.get('vix', 15.0),
    #             'us_market_change': global_cues.get('S&P 500', {}).get('pct_change', 0),
    #             'data_source': price_data.get('source', 'Unknown')
    #         }
    #         
    #         log_prediction(indicator_values, prediction, price_data.get("price", 0))
    #     except:
    #         pass


if __name__ == "__main__":
    main()
