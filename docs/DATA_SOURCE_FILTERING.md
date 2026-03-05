# Data Source Filtering for Prediction Logging

## Overview

The prediction logger now includes **data source filtering** to ensure only high-quality, real-time data is used for training the XGBoost model.

## The Problem

Training ML models on delayed data (yfinance - 15 min delay) would result in:
- ❌ Inaccurate predictions (data is stale)
- ❌ Poor model performance (trained on wrong data)
- ❌ Misleading accuracy metrics
- ❌ Unreliable trading signals

## The Solution

**Only log predictions when using real-time data sources:**
- ✅ NSE API (real-time, 0 delay)
- ✅ Angel One SmartAPI (real-time, 0 delay)
- ❌ yfinance (15 min delay - SKIP LOGGING)

## Implementation

### 1. Data Source Tracking

Every data point now includes a `data_source` field:

```python
price_data = {
    'price': 25000.50,
    'source': 'NSE API (Real-time)',  # ← Tracked
    'confidence': 'HIGH',
    ...
}
```

### 2. Logging Filter

Before logging, check data source:

```python
data_source = price_data.get('source', 'Unknown')
is_realtime = 'NSE' in data_source or 'Angel One' in data_source

if is_realtime:
    log_prediction(...)  # ✅ Log it
else:
    skip_logging()  # ❌ Skip it
```

### 3. CSV Structure

The `prediction_log.csv` now includes `data_source` column:

```csv
timestamp,rsi_14,macd_value,...,data_source,actual_outcome
2026-03-02T09:30:00,55.5,12.3,...,NSE API (Real-time),1
2026-03-02T09:31:00,56.2,12.8,...,Angel One (Real-time),-1
```

### 4. Visual Indicator

Dashboard shows real-time logging status:

**When using real-time data (NSE/Angel One):**
```
┌────────────────────────────────────────────────────────┐
│ ✅ REAL-TIME DATA ACTIVE • NSE API • Live Market Data │
│                                          ✅ LOGGING    │
└────────────────────────────────────────────────────────┘
```

**When using delayed data (yfinance):**
```
┌────────────────────────────────────────────────────────┐
│ ⚠️ USING DELAYED DATA                                  │
│ • Nifty Price (yfinance - 15 min delay)                │
│                                      🚫 NOT LOGGING    │
└────────────────────────────────────────────────────────┘
```

**When market is closed:**
```
┌────────────────────────────────────────────────────────┐
│ ✅ REAL-TIME DATA ACTIVE • NSE API • Live Market Data │
│                                          ⏸ PAUSED      │
└────────────────────────────────────────────────────────┘
```

## Data Source Priority

The system uses this fallback chain:

```
1. NSE API (Primary)
   ↓ (if fails)
2. Angel One SmartAPI (Backup)
   ↓ (if fails)
3. yfinance (Fallback - 15 min delay)
```

**Logging happens only at steps 1 and 2.**

## Benefits

### 1. Data Quality

- ✅ Only real-time data in training set
- ✅ No delayed/stale data
- ✅ Accurate price movements
- ✅ Reliable outcomes

### 2. Model Accuracy

- ✅ Trained on correct data
- ✅ Better predictions
- ✅ Higher win rate
- ✅ More profitable

### 3. Transparency

- ✅ Visual indicator shows logging status
- ✅ Know when data is being collected
- ✅ CSV includes data source for each prediction
- ✅ Can audit data quality

## Verification

### Check Logging Status

**In Dashboard:**
Look at the banner at top of page:
- Green banner with "✅ LOGGING" = Data being collected
- Yellow banner with "🚫 NOT LOGGING" = Using fallback data
- Green banner with "⏸ PAUSED" = Market closed

**In Terminal:**
```bash
# Look for these messages:
INFO:prediction_logger:Logged prediction: BULLISH at 25000.5 (source: NSE API)
INFO:prediction_logger:Skipping log - using delayed data source: yfinance
```

### Check CSV Data

```python
import pandas as pd

df = pd.read_csv('prediction_log.csv')

# Check data sources
print(df['data_source'].value_counts())

# Expected output:
# NSE API (Real-time)        45
# Angel One (Real-time)      12
# (No yfinance entries!)
```

### Verify No Delayed Data

```python
import pandas as pd

df = pd.read_csv('prediction_log.csv')

# Check for yfinance (should be 0)
yfinance_count = df['data_source'].str.contains('yfinance', case=False).sum()

if yfinance_count == 0:
    print("✅ No delayed data in training set!")
else:
    print(f"⚠️ Found {yfinance_count} delayed data points")
```

## Monitoring

### Daily Check

```bash
python quick_verify_logger.py
```

This will show:
- Total predictions logged
- Data source distribution
- Logging status

### Real-Time Monitoring

Watch dashboard banner:
- **Green + "✅ LOGGING"** = Good, collecting data
- **Yellow + "🚫 NOT LOGGING"** = Using fallback, not collecting
- **Green + "⏸ PAUSED"** = Market closed, normal

## Troubleshooting

### Issue: Not Logging Despite Real-Time Data

**Check:**
1. Is market open? (9:15-15:30 IST)
2. Is dashboard running?
3. Check terminal for "Skipping log" messages

**Fix:**
```bash
# Check market status
python -c "from data_fetcher import is_market_open; print(f'Market open: {is_market_open()}')"

# Check data source
python -c "from data_fetcher import get_live_nifty_price; print(get_live_nifty_price()['source'])"
```

### Issue: Logging Delayed Data

**This should never happen!**

If you see yfinance in `prediction_log.csv`:
1. Check prediction_logger.py - filter should block it
2. Check app.py - should check data source before logging
3. Report as bug

### Issue: Dashboard Shows Wrong Status

**Refresh the page:**
- Dashboard updates every 60 seconds
- Status indicator updates in real-time
- If stuck, refresh browser

## Configuration

No configuration needed! The filter is automatic:

```python
# In prediction_logger.py
def log_prediction(indicator_values, prediction, current_price):
    data_source = indicator_values.get('data_source', 'Unknown')
    
    # Automatic filter
    if 'yfinance' in data_source.lower():
        logger.info(f"Skipping log - using delayed data source")
        return  # Don't log
    
    # Continue logging...
```

## Impact on Data Collection

### Before (Without Filter)

```
Day 1: 50 predictions logged
  • 30 from NSE (real-time) ✅
  • 20 from yfinance (delayed) ❌
  
Problem: 40% of training data is delayed/inaccurate!
```

### After (With Filter)

```
Day 1: 30 predictions logged
  • 30 from NSE (real-time) ✅
  • 0 from yfinance (skipped) ✅
  
Result: 100% of training data is real-time/accurate!
```

**Trade-off:** Fewer predictions, but higher quality data.

## Expected Timeline

### Without Filter (Old)
- Day 1-5: Collect 300+ predictions (mixed quality)
- Day 5: Train model (on mixed data)
- Result: Lower accuracy due to delayed data

### With Filter (New)
- Day 1-7: Collect 300+ predictions (real-time only)
- Day 7: Train model (on quality data)
- Result: Higher accuracy, better predictions

**Worth the extra 2 days for better model!**

## Best Practices

### 1. Monitor Data Source

Check dashboard banner regularly:
- Should show "✅ LOGGING" during market hours
- Should show "⏸ PAUSED" outside market hours
- Should NEVER show "🚫 NOT LOGGING" during market hours

### 2. Verify Data Quality

Weekly check:
```python
import pandas as pd

df = pd.read_csv('prediction_log.csv')

# All should be real-time
print(df['data_source'].value_counts())

# Should see only:
# NSE API (Real-time)
# Angel One (Real-time)
```

### 3. Audit Training Data

Before training XGBoost:
```python
import pandas as pd

df = pd.read_csv('prediction_log.csv')

# Check data quality
print(f"Total predictions: {len(df)}")
print(f"Data sources:")
print(df['data_source'].value_counts())

# Verify no delayed data
assert not df['data_source'].str.contains('yfinance').any(), "Found delayed data!"
```

## Summary

### What Changed

1. ✅ Added `data_source` field to all data points
2. ✅ Filter in `log_prediction()` to skip delayed data
3. ✅ Visual indicator in dashboard showing logging status
4. ✅ CSV includes data source for each prediction

### Why It Matters

- ✅ Only train on real-time, accurate data
- ✅ Better model performance
- ✅ Higher prediction accuracy
- ✅ More profitable trading

### How to Verify

1. Check dashboard banner (should show "✅ LOGGING")
2. Check terminal logs (should see "Logged prediction" messages)
3. Check CSV (should have `data_source` column with NSE/Angel One)
4. Run `python quick_verify_logger.py`

### Next Steps

1. Run dashboard during market hours
2. Verify "✅ LOGGING" status in banner
3. Let it collect 300+ real-time predictions
4. Train XGBoost model on quality data
5. Enjoy better predictions!

---

**Remember:** Quality over quantity. Better to have 300 real-time predictions than 500 mixed-quality predictions!
