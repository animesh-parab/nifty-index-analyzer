# CSV/Excel Generation - Dashboard vs Logger

## Quick Answer

**BOTH the dashboard AND the standalone logger write to the same CSV file (`prediction_log.csv`).**

They both use the same `log_prediction()` function from `prediction_logger.py`.

---

## How It Works

### The CSV File:
- **File name:** `prediction_log.csv`
- **Location:** Root directory of the project
- **Format:** CSV (can be opened in Excel)

### Who Writes to It:

#### 1. Dashboard (`app.py`)
- **When:** Every time the dashboard refreshes (auto-refresh or manual)
- **Condition:** Only logs if data source is real-time (NSE or Angel One)
- **Rate limit:** Once per minute (prevents duplicates)
- **Code location:** Line 759 in `app.py`

```python
# In app.py (line 759)
log_prediction(indicator_values, prediction, price_data.get("price", 0))
```

#### 2. Standalone Logger (`standalone_logger.py`)
- **When:** Every 60 seconds (using schedule library)
- **Condition:** Only during market hours (9:15 AM - 3:30 PM IST)
- **Rate limit:** Once per minute (prevents duplicates)
- **Code location:** Line 113 in `standalone_logger.py`

```python
# In standalone_logger.py (line 113)
log_prediction(indicator_values, prediction, price_data.get("price", 0))
```

---

## The Logging Function

Both use the same function: `log_prediction()` from `prediction_logger.py`

### What It Does:
1. Checks if data source is real-time (skips yfinance delayed data)
2. Rate limits to once per 55 seconds (prevents duplicates)
3. Writes prediction to CSV with all indicators
4. Starts background thread to fill `actual_outcome` after 15 minutes

### CSV Columns (18 total):
```
timestamp, rsi_14, macd_value, macd_signal, 
ema_9, ema_21, ema_50, bb_position, atr_14, 
vix, hour, day_of_week, us_market_change,
final_direction, confidence, entry_price, 
data_source, actual_outcome
```

---

## Which One Should You Use?

### Use Dashboard (`streamlit run app.py`):
✅ If you want to see live predictions on screen
✅ If you want to monitor indicators visually
✅ If you're actively watching the market
❌ Browser tab must stay active (or auto-refresh stops)
❌ Logging stops if you close the browser

### Use Standalone Logger (`python standalone_logger.py`):
✅ If you want consistent 60-second logging
✅ If you want to run in background
✅ If you want to collect data without watching
✅ Runs independently of browser
✅ More reliable for data collection
❌ No visual interface

### Use Both Together:
✅ **RECOMMENDED for data collection**
✅ Standalone logger runs in background (consistent data)
✅ Dashboard for monitoring when you want to watch
✅ Both write to same CSV (no conflicts due to rate limiting)

---

## How They Avoid Conflicts

### Rate Limiting:
- Both check `_last_log_time` before logging
- Only logs if 55+ seconds since last log
- Uses thread lock (`_log_lock`) for thread safety
- If both try to log at same time, only one succeeds

### Example Timeline:
```
10:00:00 - Standalone logger logs ✓
10:00:30 - Dashboard tries to log ✗ (only 30s since last)
10:01:00 - Standalone logger logs ✓
10:01:30 - Dashboard tries to log ✗ (only 30s since last)
10:02:00 - Standalone logger logs ✓
```

Result: One prediction per minute, no duplicates!

---

## Viewing the Data

### In Excel:
1. Open `prediction_log.csv` in Excel
2. Data updates automatically as predictions are logged
3. Refresh Excel to see new rows

### In Python:
```python
import pandas as pd
df = pd.read_csv('prediction_log.csv')
print(df.tail(10))  # Last 10 predictions
```

### Check Status:
```bash
python verify_all_fixes.py
```

---

## Current Setup (After Fixes)

### What's Working:
✅ Standalone logger uses exact 60-second intervals (schedule library)
✅ PCR column removed (was stuck at 1.0)
✅ Outcomes backfilled (62/67 have outcomes)
✅ Both dashboard and logger write to same CSV
✅ Rate limiting prevents duplicates

### Recommended Workflow:

**For Data Collection (Month 1):**
1. Run standalone logger in background:
   ```bash
   python standalone_logger.py
   ```
2. Let it run all day during market hours
3. Optionally open dashboard to monitor
4. CSV accumulates 300+ predictions for XGBoost training

**For Live Trading (Month 2+):**
1. Run dashboard for visual monitoring:
   ```bash
   streamlit run app.py
   ```
2. Optionally run standalone logger for backup logging
3. Use dashboard predictions for actual trades

---

## Summary

| Feature | Dashboard | Standalone Logger |
|---------|-----------|-------------------|
| Writes to CSV | ✅ Yes | ✅ Yes |
| Visual interface | ✅ Yes | ❌ No |
| Runs in background | ❌ No | ✅ Yes |
| Exact 60s intervals | ❌ Variable | ✅ Exact |
| Requires browser | ✅ Yes | ❌ No |
| Best for | Monitoring | Data collection |

**Bottom line:** Use standalone logger for reliable data collection. Use dashboard when you want to watch. Both write to the same `prediction_log.csv` file.

---

**Last Updated:** March 2, 2026
**Status:** Both working, writing to same CSV with rate limiting
