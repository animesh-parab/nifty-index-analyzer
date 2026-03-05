# Failover Behavior & CSV Accumulation

## Question 1: What happens if Angel One AND NSE both fail?

### Answer: App DOES NOT CRASH - Graceful Fallback ✅

The app has a **3-tier fallback chain** with graceful degradation:

```
1. NSE API (Primary)
   ↓ (if fails)
2. Angel One SmartAPI (Backup)
   ↓ (if fails)
3. yfinance (Fallback - 15 min delay)
   ↓ (if fails)
4. Return error dict (app continues running)
```

### Code Evidence

From `data_fetcher.py` - `get_live_nifty_price()` function:

```python
def get_live_nifty_price(index="NIFTY") -> dict:
    # Try NSE first (real-time, fast, reliable)
    nse = fetch_nifty_nse(index)
    if nse and nse.get("price", 0) > 0 and nse.get("success", False):
        return nse  # ✅ NSE success
    
    # Fallback to Angel One (real-time, 0 delay)
    if USE_ANGEL_ONE:
        try:
            angel_data = fetch_nifty_angel(index)
            if angel_data and angel_data.get('price', 0) > 0:
                return angel_data  # ✅ Angel One success
        except Exception as e:
            logger.warning(f"⚠ Angel One fetch failed: {e}")
    
    # Fallback to yfinance (15-min delayed backup)
    yf_data = fetch_nifty_yfinance(index)
    if yf_data and yf_data.get("price", 0) > 0:
        return yf_data  # ✅ yfinance success
    
    # All sources failed - return error dict (app continues)
    logger.error(f"✗ All data sources failed")
    return {
        "price": 0,
        "error": "All sources failed",
        "confidence": "NONE",
        "source": "FAILED",
        "index": index
    }
```

### What Happens in Each Scenario

#### Scenario 1: NSE Works (Normal)
```
✅ NSE API → Returns real-time data
Dashboard shows: "✅ LOGGING" (if market open)
Predictions: LOGGED to CSV
```

#### Scenario 2: NSE Fails, Angel One Works
```
❌ NSE API → Fails
✅ Angel One → Returns real-time data
Dashboard shows: "✅ LOGGING" (if market open)
Predictions: LOGGED to CSV
```

#### Scenario 3: Both NSE and Angel One Fail
```
❌ NSE API → Fails
❌ Angel One → Fails
✅ yfinance → Returns delayed data (15 min)
Dashboard shows: "🚫 NOT LOGGING"
Predictions: NOT LOGGED (filtered out)
App: CONTINUES RUNNING (no crash)
```

#### Scenario 4: All Sources Fail
```
❌ NSE API → Fails
❌ Angel One → Fails
❌ yfinance → Fails
App returns: {"price": 0, "error": "All sources failed"}
Dashboard shows: Error message or 0 price
Predictions: NOT LOGGED
App: CONTINUES RUNNING (no crash)
```

### Key Points

1. **No Crash**: App never crashes due to data source failures
2. **Graceful Degradation**: Falls back through sources automatically
3. **Error Handling**: All fetch functions have try-except blocks
4. **Logging**: Terminal shows which source succeeded/failed
5. **Visual Feedback**: Dashboard banner shows data source status
6. **Prediction Filtering**: Only logs when using real-time sources (NSE or Angel One)

### Terminal Output Examples

**When NSE works:**
```
INFO:data_fetcher:Fetching live NIFTY price...
INFO:data_fetcher:✓ NSE data available for NIFTY (real-time)
INFO:prediction_logger:Logged prediction: BULLISH at 25000.5 (source: NSE API)
```

**When NSE fails, Angel One works:**
```
INFO:data_fetcher:Fetching live NIFTY price...
WARNING:data_fetcher:⚠ NSE fetch failed
INFO:data_fetcher:✓ Angel One data available for NIFTY (real-time)
INFO:prediction_logger:Logged prediction: BULLISH at 25000.5 (source: Angel One)
```

**When both fail, yfinance works:**
```
INFO:data_fetcher:Fetching live NIFTY price...
WARNING:data_fetcher:⚠ NSE fetch failed
WARNING:data_fetcher:⚠ Angel One fetch failed
INFO:data_fetcher:✓ yfinance data available for NIFTY (15-min delayed)
INFO:prediction_logger:Skipping log - using delayed data source: yfinance
```

**When all fail:**
```
INFO:data_fetcher:Fetching live NIFTY price...
WARNING:data_fetcher:⚠ NSE fetch failed
WARNING:data_fetcher:⚠ Angel One fetch failed
WARNING:data_fetcher:⚠ yfinance fetch failed
ERROR:data_fetcher:✗ All data sources failed for NIFTY
```

---

## Question 2: Is all prediction data stored in a single CSV that accumulates?

### Answer: YES - Single CSV File That Grows Forever ✅

The prediction logger uses **append mode** - all data accumulates in one file.

### Code Evidence

From `prediction_logger.py`:

```python
LOG_FILE = 'prediction_log.csv'

# Initialize CSV if it doesn't exist (ONLY ONCE)
if not os.path.exists(LOG_FILE):
    df = pd.DataFrame(columns=[...])
    df.to_csv(LOG_FILE, index=False)
    logger.info(f"Created new prediction log: {LOG_FILE}")

def log_prediction(...):
    # Prepare log entry
    log_entry = {...}
    
    # APPEND to CSV (mode='a' = append, not overwrite)
    df = pd.DataFrame([log_entry])
    df.to_csv(LOG_FILE, mode='a', header=False, index=False)
    #                   ^^^^^^^^  ^^^^^^^^^^^^
    #                   APPEND    NO HEADER (already exists)
```

### Key Points

1. **Single File**: `prediction_log.csv` - never creates new files
2. **Append Mode**: `mode='a'` - adds to end of file, never overwrites
3. **No Header Duplication**: `header=False` - only first row has headers
4. **Persistent**: File survives dashboard restarts
5. **Accumulates Forever**: Day 1 + Day 2 + ... + Day 20 all in one file

### File Behavior Over Time

**Day 1 (First Run):**
```csv
timestamp,rsi_14,macd_value,...,data_source,actual_outcome
2026-03-02T09:30:00,55.5,12.3,...,NSE API (Real-time),1
2026-03-02T09:31:00,56.2,12.8,...,NSE API (Real-time),-1
2026-03-02T09:32:00,54.8,11.9,...,Angel One (Real-time),1
```

**Day 2 (Dashboard Restart):**
```csv
timestamp,rsi_14,macd_value,...,data_source,actual_outcome
2026-03-02T09:30:00,55.5,12.3,...,NSE API (Real-time),1
2026-03-02T09:31:00,56.2,12.8,...,NSE API (Real-time),-1
2026-03-02T09:32:00,54.8,11.9,...,Angel One (Real-time),1
2026-03-03T09:30:00,57.1,13.2,...,NSE API (Real-time),1  ← NEW
2026-03-03T09:31:00,58.0,14.1,...,NSE API (Real-time),-1 ← NEW
```

**Day 20:**
```csv
timestamp,rsi_14,macd_value,...,data_source,actual_outcome
2026-03-02T09:30:00,55.5,12.3,...,NSE API (Real-time),1
... (Day 1 data)
... (Day 2 data)
... (Day 3 data)
...
... (Day 19 data)
2026-03-21T09:30:00,59.2,15.3,...,NSE API (Real-time),1  ← NEW
2026-03-21T09:31:00,60.1,16.2,...,Angel One (Real-time),-1 ← NEW
```

### File Size Estimation

**Assumptions:**
- Market hours: 6.25 hours/day (9:15 AM - 3:30 PM)
- Prediction frequency: 1 per minute
- Predictions per day: ~375 (6.25 hours × 60 minutes)
- Row size: ~150 bytes (19 columns)

**File Size Over Time:**
```
Day 1:  375 rows × 150 bytes = ~56 KB
Day 5:  1,875 rows = ~280 KB
Day 10: 3,750 rows = ~560 KB
Day 20: 7,500 rows = ~1.1 MB
Day 30: 11,250 rows = ~1.7 MB
```

**Conclusion:** Even after 30 days, file is only ~1.7 MB - very manageable!

### XGBoost Training

When you're ready to train (after 10-20 days):

```python
import pandas as pd
from xgb_model import train_model

# Load ALL accumulated data (all 20 days)
df = pd.read_csv('prediction_log.csv')

print(f"Total predictions: {len(df)}")
# Output: Total predictions: 7500 (20 days × 375/day)

print(f"With outcomes: {df['actual_outcome'].notna().sum()}")
# Output: With outcomes: 7500 (all have outcomes after 15 min)

# Train on ALL data
train_model()  # Uses all rows in prediction_log.csv
```

### Benefits of Single File Approach

1. **Simple**: One file to manage, no file rotation logic
2. **Complete History**: All data in one place for analysis
3. **Easy Training**: Just load one CSV file
4. **No Data Loss**: Never overwrites or deletes old data
5. **Portable**: Easy to backup, share, or move
6. **Chronological**: Natural time series ordering

### File Management

**To start fresh (if needed):**
```bash
# Backup old data
mv prediction_log.csv prediction_log_backup_2026-03-02.csv

# Dashboard will create new file automatically
streamlit run app.py
```

**To analyze specific date range:**
```python
import pandas as pd

df = pd.read_csv('prediction_log.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Filter to specific dates
march_data = df[df['timestamp'].dt.month == 3]
week1_data = df[df['timestamp'].dt.day <= 7]
```

**To check file size:**
```bash
# Windows
dir prediction_log.csv

# Linux/Mac
ls -lh prediction_log.csv
```

---

## Summary

### Question 1: App Crash Behavior
✅ **NO CRASH** - Graceful fallback through 3 sources
- NSE fails → Try Angel One
- Angel One fails → Try yfinance
- All fail → Return error dict, app continues
- Dashboard shows appropriate status banner
- Predictions only logged when using real-time sources

### Question 2: CSV Accumulation
✅ **SINGLE FILE** - Accumulates forever
- File: `prediction_log.csv`
- Mode: Append (`mode='a'`)
- Behavior: Day 1 + Day 2 + ... + Day 20 all in one file
- Size: ~1.1 MB after 20 days (very manageable)
- Training: Load entire file for XGBoost

### Your Plan is Perfect ✅

Your plan to run for 10-20 days and feed all data to XGBoost is exactly how the system is designed:

1. **Day 1-20**: Dashboard runs, predictions accumulate in `prediction_log.csv`
2. **Day 20**: File has ~7,500 predictions with outcomes
3. **Training**: Run `python xgb_model.py` - trains on all 7,500 samples
4. **Result**: Well-trained model with diverse market conditions

### Verification Commands

**Check if file is accumulating:**
```bash
# Count rows (should increase daily)
python -c "import pandas as pd; print(len(pd.read_csv('prediction_log.csv')))"
```

**Check date range:**
```bash
python -c "import pandas as pd; df = pd.read_csv('prediction_log.csv'); print(f'First: {df.timestamp.iloc[0]}'); print(f'Last: {df.timestamp.iloc[-1]}')"
```

**Check file size:**
```bash
python -c "import os; print(f'{os.path.getsize(\"prediction_log.csv\") / 1024:.1f} KB')"
```

---

## Conclusion

Both aspects are handled correctly:

1. ✅ **No crash on data source failure** - graceful fallback with visual feedback
2. ✅ **Single accumulating CSV** - perfect for your 10-20 day collection plan

The system is production-ready for long-term data collection!
