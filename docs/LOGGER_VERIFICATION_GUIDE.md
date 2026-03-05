# Prediction Logger Verification Guide

## Quick Verification Checklist

After running the dashboard for 20+ minutes, verify these 3 things:

### ✅ 1. CSV Writing Works

```bash
# Check if file exists and has data
python -c "import pandas as pd; df = pd.read_csv('prediction_log.csv'); print(f'Total predictions: {len(df)}'); print(df.tail())"
```

**Expected Output:**
```
Total predictions: 5
   timestamp  rsi_14  macd_value  ...  confidence  entry_price  actual_outcome
0  2026-03-02T09:30:00  55.5  12.3  ...  68  25000.5  NaN
1  2026-03-02T09:31:00  56.2  12.8  ...  72  25010.2  NaN
...
```

**What to Check:**
- ✅ File exists: `prediction_log.csv`
- ✅ Has rows (one per prediction)
- ✅ Has all 18 columns
- ✅ `actual_outcome` is NaN initially (will be filled after 15 min)

### ✅ 2. Outcome Tracking Works

Wait 20 minutes after first prediction, then check:

```bash
python -c "import pandas as pd; df = pd.read_csv('prediction_log.csv'); print(f'Total: {len(df)}'); print(f'With outcomes: {df[\"actual_outcome\"].notna().sum()}')"
```

**Expected Output:**
```
Total: 5
With outcomes: 2
```

**What to Check:**
- ✅ Some predictions have `actual_outcome` filled (1, -1, or 0)
- ✅ Recent predictions (<15 min old) still have NaN
- ✅ Old predictions (>15 min old) have outcomes

### ✅ 3. Background Thread Works

Check terminal logs while dashboard is running:

```
INFO:prediction_logger:Logged prediction: BULLISH at 25000.5
... (15 minutes later) ...
INFO:prediction_logger:Updated outcome: 1 (price change: +0.25%)
```

**What to Check:**
- ✅ "Logged prediction" appears when prediction is made
- ✅ "Updated outcome" appears 15 minutes later
- ✅ No error messages in logs

## Common Issues & Fixes

### Issue 1: CSV File Empty or Not Created

**Symptoms:**
- `prediction_log.csv` doesn't exist
- File exists but has 0 rows

**Causes:**
- Dashboard not running during market hours
- Logging code not integrated into app.py
- Permissions issue

**Fix:**
```bash
# Check if file exists
ls -la prediction_log.csv

# Check permissions
chmod 644 prediction_log.csv

# Verify integration in app.py
grep -n "log_prediction" app.py
```

### Issue 2: Outcomes Never Get Filled

**Symptoms:**
- All `actual_outcome` values are NaN
- Even after 30+ minutes

**Causes:**
- Background thread not starting
- yfinance API failing
- Timestamp matching issue

**Fix:**

Check logs for errors:
```bash
# Look for outcome update errors
grep "Error checking outcome" logs.txt
```

Test manually:
```python
from prediction_logger import _check_outcome_later
from datetime import datetime

# Test outcome checking (will take 15 min)
_check_outcome_later(datetime.now(), 25000.0)
```

### Issue 3: Timestamp Matching Fails

**Symptoms:**
- Outcomes logged but not written to CSV
- "Updated outcome" in logs but CSV unchanged

**Cause:**
- Timestamp format mismatch
- Floating point precision issues

**Fix:**

The logger uses ISO format timestamps. Verify:
```python
import pandas as pd
df = pd.read_csv('prediction_log.csv')
print(df['timestamp'].iloc[0])  # Should be: 2026-03-02T09:30:00.123456
```

### Issue 4: Only Works in Live Mode

**This is NOT an issue!**

The logger works in:
- ✅ Paper trading mode
- ✅ Live trading mode
- ✅ Dashboard-only mode (no trading)

It logs predictions regardless of trading mode.

## Detailed Verification Steps

### Step 1: Run Dashboard for 5 Minutes

```bash
streamlit run app.py
```

Wait 5 minutes, then check:

```bash
python test_prediction_logger.py
```

Expected:
- ✅ CSV file created
- ✅ Multiple rows logged
- ✅ All outcomes are NaN (too early)

### Step 2: Wait 20 Minutes Total

Keep dashboard running. After 20 minutes total:

```bash
python test_prediction_logger.py
```

Expected:
- ✅ More rows logged
- ✅ First few predictions have outcomes filled
- ✅ Recent predictions still NaN

### Step 3: Check Outcome Distribution

After 1 hour of running:

```python
import pandas as pd
df = pd.read_csv('prediction_log.csv')

# Filter predictions with outcomes
with_outcomes = df[df['actual_outcome'].notna()]

print(f"Total predictions: {len(df)}")
print(f"With outcomes: {len(with_outcomes)}")
print(f"\nOutcome distribution:")
print(f"UP (+1): {(with_outcomes['actual_outcome'] == 1).sum()}")
print(f"DOWN (-1): {(with_outcomes['actual_outcome'] == -1).sum()}")
print(f"SIDEWAYS (0): {(with_outcomes['actual_outcome'] == 0).sum()}")
```

Expected:
- ✅ ~50-70% of predictions have outcomes
- ✅ Reasonable distribution (not all same outcome)
- ✅ UP and DOWN outcomes present

## Understanding the 15-Minute Lookback

### How It Works

```
9:30:00 AM - Prediction made, logged to CSV
             Entry price: 25,000
             Outcome: NaN (pending)
             Background thread starts

9:45:00 AM - Thread wakes up (15 min later)
             Fetches current price: 25,050
             Calculates change: +0.2%
             Outcome: 1 (UP)
             Updates CSV with outcome
```

### Verification

Check a specific prediction:

```python
import pandas as pd
from datetime import datetime, timedelta

df = pd.read_csv('prediction_log.csv')

# Get first prediction
first = df.iloc[0]
pred_time = datetime.fromisoformat(first['timestamp'])
expected_check_time = pred_time + timedelta(minutes=15)

print(f"Prediction time: {pred_time}")
print(f"Expected check time: {expected_check_time}")
print(f"Entry price: {first['entry_price']}")
print(f"Outcome: {first['actual_outcome']}")

# If outcome is filled, it worked!
if pd.notna(first['actual_outcome']):
    print("✅ 15-minute lookback working!")
else:
    current_time = datetime.now()
    if current_time < expected_check_time:
        print(f"⏳ Still waiting (check at {expected_check_time})")
    else:
        print(f"❌ Should have been filled by now")
```

## Monitoring During Live Use

### Dashboard Logs

Watch for these messages:

```
INFO:prediction_logger:Logged prediction: BULLISH at 25000.5
INFO:prediction_logger:Updated outcome: 1 (price change: +0.25%)
INFO:prediction_logger:Updated outcome: -1 (price change: -0.15%)
INFO:prediction_logger:Updated outcome: 0 (price change: +0.05%)
```

### CSV Growth

Check file size grows over time:

```bash
# Check file size every 5 minutes
watch -n 300 'wc -l prediction_log.csv'
```

Expected:
- Grows by ~5-10 rows per hour during market hours
- Stops growing outside market hours

### Outcome Fill Rate

After 1 hour:

```python
import pandas as pd
df = pd.read_csv('prediction_log.csv')

total = len(df)
with_outcome = df['actual_outcome'].notna().sum()
fill_rate = (with_outcome / total * 100) if total > 0 else 0

print(f"Outcome fill rate: {fill_rate:.1f}%")

# Should be 50-70% after 1 hour
# (recent predictions still pending)
```

## Troubleshooting Commands

### Check if logger is imported in app.py

```bash
grep -A 5 "from prediction_logger import" app.py
```

Should show:
```python
from prediction_logger import log_prediction, extract_indicator_values
```

### Check if logging is called

```bash
grep -A 10 "log_prediction(" app.py
```

Should show the logging call in the prediction section.

### Check background threads

While dashboard is running:

```python
import threading
print(f"Active threads: {threading.active_count()}")
print(f"Thread names: {[t.name for t in threading.enumerate()]}")
```

Should show daemon threads for outcome checking.

### Force outcome check (for testing)

```python
from prediction_logger import _check_outcome_later
from datetime import datetime

# This will wait 15 minutes then update
_check_outcome_later(datetime.now(), 25000.0)
```

## Success Criteria

After 1 hour of running dashboard:

- ✅ `prediction_log.csv` exists
- ✅ Has 30-60 rows (depends on refresh rate)
- ✅ 50-70% of predictions have outcomes filled
- ✅ Outcomes are distributed (not all same)
- ✅ No errors in logs
- ✅ File size growing over time

## Next Steps

Once verified:

1. Let dashboard run for 3-5 days
2. Collect 300+ predictions with outcomes
3. Run hourly performance analysis
4. Train XGBoost model
5. Monitor and retrain weekly

## Quick Test Script

Save this as `quick_verify.py`:

```python
import pandas as pd
import os
from datetime import datetime, timedelta

LOG_FILE = 'prediction_log.csv'

print("="*70)
print("QUICK VERIFICATION")
print("="*70)

if not os.path.exists(LOG_FILE):
    print("❌ prediction_log.csv not found")
    print("   Run dashboard first to create it")
    exit(1)

df = pd.read_csv(LOG_FILE)
total = len(df)
with_outcome = df['actual_outcome'].notna().sum()

print(f"\n✅ File exists: {LOG_FILE}")
print(f"✅ Total predictions: {total}")
print(f"✅ With outcomes: {with_outcome}")

if total == 0:
    print("\n⚠️ No predictions logged yet")
    print("   Run dashboard during market hours")
elif with_outcome == 0:
    first_time = datetime.fromisoformat(df['timestamp'].iloc[0])
    wait_until = first_time + timedelta(minutes=15)
    now = datetime.now()
    
    if now < wait_until:
        wait_min = (wait_until - now).total_seconds() / 60
        print(f"\n⏳ Waiting for first outcome")
        print(f"   Check again in {wait_min:.0f} minutes")
    else:
        print(f"\n❌ No outcomes filled yet (should have by now)")
        print(f"   Check logs for errors")
else:
    fill_rate = (with_outcome / total * 100)
    print(f"✅ Outcome fill rate: {fill_rate:.1f}%")
    
    if fill_rate > 40:
        print(f"\n✅ Logger working correctly!")
    else:
        print(f"\n⚠️ Low fill rate (expected 50-70%)")

print("="*70)
```

Run with:
```bash
python quick_verify.py
```
