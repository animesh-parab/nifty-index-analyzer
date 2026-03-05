# Data Collection Guide - Complete Reference

## Quick Start

### Start Logger (9:15 AM):
```bash
python standalone_logger.py
```

### Check Status:
```bash
python check_current_status.py
```

### Stop Logger (3:30 PM):
Press `Ctrl+C` in PowerShell window

### Backfill Outcomes:
```bash
python backfill_outcomes.py
```

### Generate Report:
```bash
python end_of_day_report.py
```

---

## Current Status (March 2, 2026)

### Day 1 Results:
- **168 clean predictions** collected
- **100% NSE API** (real-time data)
- **Need:** 132 more for XGBoost training (target: 300+)

### Data Quality:
✅ Duplicates removed (was 194, now 168)
✅ 1 entry per minute
✅ Outcomes filled (94%+ complete)
✅ All real-time data (no delayed feeds)

---

## System Configuration

### Fixed Issues:
1. ✅ **Logging interval:** Exact 60s using schedule library
2. ✅ **PCR column:** Removed (APIs unreliable)
3. ✅ **Outcomes:** Backfill script working
4. ✅ **Duplicates:** Removed from data
5. ✅ **Multiple loggers:** Prevented

### CSV Structure (18 columns):
```
timestamp, rsi_14, macd_value, macd_signal, 
ema_9, ema_21, ema_50, bb_position, atr_14, 
vix, hour, day_of_week, us_market_change,
final_direction, confidence, entry_price, 
data_source, actual_outcome
```

---

## API Usage

### Primary: NSE API (100% of data)
- Live Nifty price
- Candle data (OHLC)
- India VIX
- Global cues (US markets)

**Rate:** 4 calls per minute
**Limit:** 600 calls per minute
**Usage:** <1% of capacity ✅

### Fallback: Angel One SmartAPI
- Only used if NSE fails
- Same data sources
- Rate: 3 calls per minute

### Outcome Checking: yfinance
- Used after 15 minutes
- 1 call per prediction
- No rate limits

---

## Tomorrow's Plan (March 3)

### Timeline:
- **Start:** 9:15 AM IST
- **End:** 3:30 PM IST
- **Goal:** Collect 132+ more predictions
- **Total after:** 300+ predictions ✅

### Steps:
1. Start logger at 9:15 AM
2. Verify working (check after 2-3 min)
3. Keep laptop awake until 3:30 PM
4. Stop logger at 3:30 PM
5. Backfill outcomes
6. Generate report
7. **Train XGBoost model** (if 300+)

---

## Troubleshooting

### Logger not logging:
- Check if market is open (9:15 AM - 3:30 PM IST, Mon-Fri)
- Verify NSE API is accessible
- Check PowerShell for errors

### Outcomes not filling:
```bash
python backfill_outcomes.py
```

### Duplicates appearing:
- Only run 1 logger instance
- Use `start_single_logger.py` to prevent duplicates

### Check intervals:
```bash
python check_intervals.py
```

---

## Files Reference

### Main Scripts:
- `standalone_logger.py` - Main data collection script
- `prediction_logger.py` - Logging functions
- `data_fetcher.py` - API data fetching
- `indicators.py` - Technical indicators
- `ai_engine_consensus.py` - Prediction engine

### Utility Scripts:
- `check_current_status.py` - Quick status check
- `backfill_outcomes.py` - Fill missing outcomes
- `remove_duplicates.py` - Clean duplicate entries
- `end_of_day_report.py` - Daily summary
- `verify_all_stopped.py` - Check all processes stopped

### Data Files:
- `prediction_log.csv` - Main data file
- `backups/prediction_log_backup_*.csv` - Backups

---

## Rate Limits - Safe Usage

| Setup | API Calls/Min | Rate Limit | Usage % | Safe? |
|-------|---------------|------------|---------|-------|
| Logger only | 4 | 600 | 0.7% | ✅ Yes |
| Dashboard only | 8 | 600 | 1.3% | ✅ Yes |
| Both together | 12 | 600 | 2% | ✅ Yes |

**Conclusion:** Even with both running, you're using <2% of API capacity.

---

## XGBoost Training

### When Ready (300+ predictions):
```bash
python xgb_model.py
```

### What It Does:
1. Loads all predictions from CSV
2. Trains XGBoost model
3. Saves trained model
4. Shows accuracy metrics
5. Displays feature importance

### Requirements:
- 300+ predictions with outcomes
- Clean data (no duplicates)
- Real-time data sources

---

## Data Collection Best Practices

### Do:
✅ Run single logger instance
✅ Keep laptop awake during market hours
✅ Backfill outcomes after market close
✅ Remove duplicates if they appear
✅ Check status occasionally

### Don't:
❌ Run multiple logger instances
❌ Put laptop to sleep during collection
❌ Stop logger during market hours
❌ Delete CSV file or backups

---

**Last Updated:** March 2, 2026 3:40 PM IST
**Status:** Day 1 complete - 168/300 predictions
**Next:** Continue tomorrow at 9:15 AM
