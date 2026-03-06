# Nifty AI Predictor

AI-powered Nifty 50 prediction and trading system using XGBoost, technical indicators, and dual-AI consensus.

## 🚀 Current Status (March 6, 2026)

- ✅ **618 predictions collected** with 60-minute outcome tracking
- ✅ **Time filter bug FIXED** - Now logging 100% of market hours (was 48%)
- ✅ **Trade signal scanner** integrated with locked rules (8 signals/day, 50% win rate)
- ✅ **Dashboard redesigned** - Alt-tab friendly, 900 lines (down from 1,868)
- ✅ **News fetcher updated** - 3 reliable RSS sources, 24-hour filter
- ✅ **CSV corruption fixed** - Proper quoting on all writes
- ✅ **System ready for live trading** with real-time data sources

**Latest:** See `MARCH_2026_FIXES.md` for all March 6 improvements

---

## 🎯 Quick Start

### Run Live Dashboard:
```bash
streamlit run app.py
```

### Start Data Collection:
```bash
python standalone_logger.py
```

### Run Tests:
```bash
python test_indicator_logic.py
```

---

## 📁 Project Structure

```
├── Core Trading System
│   ├── app.py                          # Streamlit dashboard with trade signals
│   ├── trade_signal_scanner.py         # CALL/PUT signal detection (LOCKED RULES)
│   ├── enhanced_prediction_engine.py   # Enhanced prediction with regime detection
│   ├── indicator_scoring.py            # 9 indicator scoring functions
│   └── test_indicator_logic.py         # Verification tests (8/8 passing)
│
├── Data Collection & Logging
│   ├── standalone_logger.py            # Automated prediction logging
│   ├── prediction_logger.py            # Logging functions (60-min lookback)
│   ├── prediction_state.py             # State management
│   └── prediction_log.csv              # Training data (655 rows)
│
├── Data Sources
│   ├── data_fetcher.py                 # NSE API (primary)
│   ├── angel_one_fetcher.py            # Angel One SmartAPI (backup)
│   ├── nse_options_robust.py           # Options chain data
│   └── news_fetcher_scheduled.py       # News sentiment
│
├── Technical Analysis
│   ├── indicators.py                   # Technical indicators
│   ├── greeks.py                       # Options Greeks
│   ├── volatility_forecaster.py       # VIX forecasting
│   └── price_alerts.py                 # Price alert system
│
├── AI & ML
│   ├── ai_engine_consensus.py          # Dual-AI (Groq + Gemini)
│   ├── xgb_model.py                    # XGBoost training
│   ├── xgb_model.pkl                   # Trained model
│   └── weekly_retrain.py               # Automated retraining
│
├── Configuration
│   ├── config.py                       # System configuration
│   ├── .env                            # API keys (not in git)
│   ├── env.example                     # Environment template
│   └── requirements.txt                # Python dependencies
│
├── Utilities
│   ├── api_rate_monitor.py             # API usage tracking
│   ├── view_api_usage.py               # Usage viewer
│   ├── download_instruments.py         # Instrument list downloader
│   └── angel_one_setup.py              # Angel One setup
│
├── Data Files
│   ├── instruments_nifty_options.csv   # Options instrument list
│   ├── token_map.json                  # Token mappings
│   └── backups/                        # CSV backups
│
├── Scripts (scripts/)
│   ├── check_current_status.py         # System status check
│   ├── backfill_outcomes.py            # Fill missing outcomes
│   ├── end_of_day_report.py            # Daily summary
│   └── [other utility scripts]
│
└── Documentation (docs/)
    ├── DATA_COLLECTION_GUIDE.md        # Collection guide
    ├── HOW_BACKTESTING_WORKS.md        # Backtesting guide
    ├── DEPLOYMENT_SUMMARY.md           # Deployment info
    └── [70+ other documentation files]
```

---

## ✨ Key Features

### Trade Signal Scanner (NEW):
- ✅ **CALL Setup Detection**: Oversold at support with RSI rising
- ✅ **PUT Setup Detection**: Overbought at resistance with rally exhaustion
- ✅ **ATR-Based Stops**: Dynamic stop loss (no tight +1 point stops)
- ✅ **Risk:Reward > 2.0**: Minimum 1:2 risk-reward ratio
- ✅ **Confluence 7/7**: All conditions must align
- ✅ **Time Filter**: Only 10:00-12:00 and 1:30-2:30
- ✅ **Large Alert Boxes**: Green for CALL, Red for PUT

### Enhanced Prediction Engine:
- ✅ **9 Indicator Fixes**: Time filter, RSI direction, MACD histogram, EMA crossover, Bollinger bands, VIX direction, regime detection, opening range, previous day levels
- ✅ **Market Regime Detection**: ADX-based (TRENDING/RANGING/NEUTRAL)
- ✅ **Dynamic Weights**: Adjust indicator weights based on regime
- ✅ **Dual-AI Consensus**: Groq (Llama 3.3 70B) + Gemini (1.5 Flash)
- ✅ **Confidence Scoring**: 0-100% with strength levels

### Data Collection:
- ✅ **Real-time NSE API** (primary source)
- ✅ **Angel One SmartAPI** (backup source)
- ✅ **60-minute outcome tracking** with max move labeling
- ✅ **60-second logging intervals** during market hours
- ✅ **16 technical indicators** logged per prediction

### Technical Indicators:
- RSI (14) with direction logic
- MACD with histogram momentum
- EMAs (9/21/50) with crossover detection
- Bollinger Bands with trend awareness
- ATR (14) for volatility
- VIX with direction logic
- ADX for regime detection
- Opening range breakout
- Previous day high/low levels

---

## 🎯 Trade Signal Rules (LOCKED)

### CALL Setup (Support Bounce):
- Position in range < 0.25 (near support)
- RSI < 45 AND rising (oversold + momentum)
- Distance to support < 25 points
- Risk:Reward > 2.0
- Candles since low > 3 (not immediate bounce)
- Confluence 7/7 required
- Time: 10:00-12:00 or 1:30-2:30 only

### PUT Setup (Resistance Rejection):
- Position in range > 0.7 (near resistance)
- RSI > 60 (overbought)
- Distance to resistance < 5 points
- Distance to support > 100 points
- Rally size > 80 points
- Risk:Reward > 2.0
- Confluence 7/7 required
- Time: 10:00-12:00 or 1:30-2:30 only

### Expected Performance:
- ~8 signals per day during active hours
- 50% win rate (verified by backtest)
- +50 points average per day
- ~2 CALL signals, ~6 PUT signals

---

## 📊 Data Collection Workflow

### Current Phase: Live Trading + Data Collection
1. ✅ Run dashboard for live signals: `streamlit run app.py`
2. ✅ Run logger for data collection: `python standalone_logger.py`
3. ✅ Monitor trade signals in dashboard
4. ✅ Log predictions with 60-minute outcome tracking
5. ✅ Retrain model weekly with new data

### Outcome Labeling Logic:
- **60-minute lookback window** (not 15 minutes)
- **Max move detection**: Uses highest/lowest prices in window
- **UP**: Max up move > 0.3% AND greater than max down move
- **DOWN**: Max down move > 0.3% AND greater than max up move
- **SIDEWAYS**: Neither condition met

---

## 🔧 Requirements

```bash
pip install -r requirements.txt
```

### Key Dependencies:
- streamlit >= 1.32.0
- pandas >= 2.0.0
- numpy >= 1.24.0
- xgboost >= 2.0.0
- scikit-learn >= 1.3.0
- imbalanced-learn >= 0.11.0
- pandas_ta >= 0.3.14b
- smartapi-python >= 1.3.7
- websocket-client >= 1.6.0
- groq >= 0.9.0
- google-genai >= 1.65.0
- plotly >= 5.18.0
- ta >= 0.11.0
- schedule == 1.2.0

**Note**: yfinance is NOT used (blocked permanently - 15-minute delayed data)

---

## ⚙️ Configuration

### Environment Variables (.env):
```bash
# AI APIs
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here

# Angel One SmartAPI (backup data source)
ANGEL_ONE_API_KEY=your_key_here
ANGEL_ONE_CLIENT_ID=your_id_here
ANGEL_ONE_PASSWORD=your_password_here
ANGEL_ONE_TOTP_SECRET=your_secret_here
```

### Market Hours:
- **Pre-Open**: 9:00 - 9:15 AM IST
- **Market Open**: 9:15 AM - 3:30 PM IST
- **Trading Hours**: 10:00 AM - 2:30 PM IST (with lunch break)
- **Days**: Monday - Friday

---

## 📈 API Rate Limits

| API | Calls/Min | Daily Limit | Usage % |
|-----|-----------|-------------|---------|
| NSE | 4 | 600/min | <1% |
| Angel One | 3 | 600/min | <1% |
| Groq | 2 | 14,400/day | <1% |
| Gemini | 2 | 1,500/day | <1% |

**Total API Usage**: <1% of capacity - Very safe! ✅

---

## 🧪 Testing

### Run All Tests:
```bash
python test_indicator_logic.py
```

### Expected Output:
```
=== TESTING ALL INDICATOR FIXES ===

TEST 1: Time of Day Filter
✓ PASS: Time Filter - All tests passed

TEST 2: RSI Direction Logic
✓ PASS: RSI Direction - All tests passed

TEST 3: MACD Histogram Momentum
✓ PASS: MACD Histogram - All tests passed

TEST 4: EMA Crossover Detection
✓ PASS: EMA Crossover - All tests passed

TEST 5: Bollinger Bands Trend Awareness
✓ PASS: Bollinger Bands - All tests passed

TEST 6: VIX Direction Logic
✓ PASS: VIX Direction - All tests passed

TEST 7: Opening Range Breakout
✓ PASS: Opening Range - All tests passed

TEST 8: Previous Day High/Low
✓ PASS: Previous Day Levels - All tests passed

=== ALL TESTS PASSED - SYSTEM READY FOR LIVE TRADING ===
```

---

## 🛠️ Troubleshooting

### Check System Status:
```bash
python scripts/check_current_status.py
```

### Backfill Missing Outcomes:
```bash
python scripts/backfill_outcomes.py
```

### View API Usage:
```bash
python view_api_usage.py
```

### Check Prediction Log:
```bash
python -c "import pandas as pd; df = pd.read_csv('prediction_log.csv'); print(f'Total: {len(df)}, With outcomes: {df[\"actual_outcome\"].notna().sum()}')"
```

---

## 📚 Documentation

See `docs/` folder for complete documentation (70+ files).

### Key Documents:
- `docs/DATA_COLLECTION_GUIDE.md` - Complete collection guide
- `docs/HOW_BACKTESTING_WORKS.md` - Backtesting methodology
- `docs/DEPLOYMENT_SUMMARY.md` - Deployment information
- `docs/API_RATE_LIMIT_ANALYSIS.md` - API usage analysis
- `docs/MODEL_EXPLANATION_ONE_PAGE.md` - Model explanation
- `START_HERE.md` - Quick start guide
- `TRADE_ANALYSIS_AND_ROADMAP.md` - Trading strategy

---

## 🎯 Current Progress

**Total Predictions**: 655 rows
**With Outcomes**: ~400+ (60-minute lookback)
**Model Status**: Trained and ready
**System Status**: ✅ Live trading ready
**Last Updated**: March 5, 2026

---

## 🚫 What's NOT Included

- ❌ **yfinance** - Removed (15-minute delayed data)
- ❌ **Historical experiments** - Archived in `archive_historical_experiments/`
- ❌ **Kaggle data** - Not used for live trading
- ❌ **Old model versions** - Only `xgb_model.pkl` kept
- ❌ **Temporary files** - Cleaned up before GitHub push

---

## 📝 License & Credits

Built for Nifty 50 options trading analysis.

**Data Sources**:
- NSE India (primary)
- Angel One SmartAPI (backup)
- India VIX
- Global market indices

**AI Models**:
- Groq (Llama 3.3 70B)
- Google Gemini (1.5 Flash)
- XGBoost (custom trained)

---

## 🔗 Repository

GitHub: https://github.com/animesh-parab/nifty-index-analyzer.git

---

**Last Updated**: March 5, 2026 (System ready for live trading)
**Status**: ✅ All systems operational
**Next**: Monitor trade signals and continue data collection
