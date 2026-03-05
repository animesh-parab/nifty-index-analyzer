# Nifty AI Predictor

AI-powered Nifty 50 prediction system using XGBoost and technical indicators.

## Quick Start

### Today's Status (March 2, 2026):
- ✅ 168 predictions collected
- ✅ Data cleaned (duplicates removed)
- ⏳ Need 132 more for XGBoost training

### Tomorrow (March 3):

**Start data collection at 9:15 AM:**
```bash
python standalone_logger.py
```

**Check status:**
```bash
python scripts/check_current_status.py
```

**After market close (3:30 PM):**
```bash
python scripts/backfill_outcomes.py
python scripts/end_of_day_report.py
```

---

## Project Structure

```
├── Core Scripts
│   ├── standalone_logger.py      # Data collection (run this!)
│   ├── prediction_logger.py      # Logging functions
│   ├── data_fetcher.py           # API data fetching
│   ├── indicators.py             # Technical indicators
│   ├── ai_engine_consensus.py    # Prediction engine
│   └── xgb_model.py              # XGBoost training
│
├── Dashboard
│   ├── app.py                    # Streamlit dashboard
│   └── backtest_ui.py            # Backtesting UI
│
├── Data Files
│   ├── prediction_log.csv        # Main training data
│   └── backups/                  # CSV backups
│
├── Utility Scripts (scripts/)
│   ├── check_current_status.py   # Status check
│   ├── backfill_outcomes.py      # Fill missing outcomes
│   ├── remove_duplicates.py      # Clean duplicates
│   └── end_of_day_report.py      # Daily summary
│
└── Documentation (docs/)
    ├── DATA_COLLECTION_GUIDE.md  # Main guide
    ├── README_DOCS.md            # Doc index
    └── [40+ other docs]
```

---

## Features

### Data Collection:
- ✅ Real-time NSE API data
- ✅ Angel One SmartAPI fallback
- ✅ Automatic outcome tracking (15-min delay)
- ✅ 60-second logging intervals
- ✅ 16 technical indicators

### Prediction Engine:
- AI consensus (Groq + Gemini)
- Rule-based fallback
- Confidence scoring
- Entry price tracking

### Technical Indicators:
- RSI, MACD, EMAs (9/21/50)
- Bollinger Bands, ATR
- VIX, US market correlation
- Hour and day-of-week features

---

## Data Collection Workflow

### Month 1: Collect Training Data
1. Run logger daily during market hours
2. Collect 300+ predictions with outcomes
3. Train XGBoost model
4. Validate accuracy

### Month 2+: Live Trading
1. Use trained model for predictions
2. Continue logging for model improvement
3. Retrain periodically with new data

---

## Requirements

```bash
pip install -r requirements.txt
```

Key dependencies:
- pandas, numpy
- yfinance
- streamlit
- xgboost
- schedule
- requests

---

## Configuration

### Environment Variables (.env):
```
GROQ_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
ANGEL_ONE_API_KEY=your_key_here
ANGEL_ONE_CLIENT_ID=your_id_here
ANGEL_ONE_PASSWORD=your_password_here
ANGEL_ONE_TOTP_SECRET=your_secret_here
```

### Market Hours:
- Open: 9:15 AM IST
- Close: 3:30 PM IST
- Days: Monday - Friday

---

## API Rate Limits

| API | Calls/Min | Limit | Usage % |
|-----|-----------|-------|---------|
| NSE | 4 | 600 | 0.7% |
| Angel One | 3 | 600 | 0.5% |
| yfinance | 1/15min | Unlimited | 0% |

**Total:** <1% of capacity - Very safe! ✅

---

## Troubleshooting

### Logger not working:
```bash
python scripts/check_current_status.py
```

### Outcomes not filling:
```bash
python scripts/backfill_outcomes.py
```

### Duplicates in data:
```bash
python scripts/remove_duplicates.py
```

### Check intervals:
```bash
python scripts/check_intervals.py
```

---

## Documentation

See `docs/README_DOCS.md` for complete documentation index.

Key docs:
- `docs/DATA_COLLECTION_GUIDE.md` - Complete collection guide
- `docs/TOMORROW_RESTART.md` - Tomorrow's plan
- `docs/THREE_ISSUES_FIXED.md` - Recent fixes

---

## Current Progress

**Day 1 (March 2):** 168/300 predictions ✅
**Day 2 (March 3):** Target 132+ more
**Total Target:** 300+ for XGBoost training

---

## License & Credits

Built for Nifty 50 options trading analysis.
Uses NSE API, Angel One SmartAPI, and yfinance.

---

**Last Updated:** March 2, 2026 3:40 PM IST
**Status:** Day 1 complete, ready for Day 2
**Next:** Run logger tomorrow at 9:15 AM
