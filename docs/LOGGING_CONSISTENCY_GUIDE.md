# Logging Consistency Guide

## Issue: Inconsistent 1-Minute Logging

**Problem:** Predictions should log every 60 seconds, but gaps of 78s, 187s, 254s are observed.

**Root Cause:** Streamlit's `st_autorefresh` pauses when browser tab is inactive/minimized.

---

## Solutions

### Option 1: Keep Dashboard Tab Active (Simplest)
**Pros:**
- No code changes needed
- Dashboard visible for monitoring

**Cons:**
- Requires browser tab to stay active
- Pauses if you switch tabs or minimize

**How to use:**
1. Keep browser tab with dashboard open and visible
2. Don't minimize the window
3. Don't switch to other tabs for long periods

---

### Option 2: Run Standalone Logger (Recommended)
**Pros:**
- Runs independently of dashboard
- Consistent 60-second intervals
- Works even if dashboard is closed
- More reliable for data collection

**Cons:**
- Requires separate terminal/process
- Duplicates some dashboard functionality

**How to use:**
```bash
# In a separate terminal
python standalone_logger.py
```

This will:
- Run in the background
- Log predictions every 60 seconds
- Only during market hours (9:15 AM - 3:30 PM)
- Skip weekends automatically
- Use real-time data sources (NSE/Angel One)

**Output:**
```
======================================================================
STANDALONE PREDICTION LOGGER
======================================================================
This will log predictions every 60 seconds during market hours
Press Ctrl+C to stop
======================================================================

[10:30:00] Market OPEN - Generating prediction...
Fetching data...
✅ Logged: BULLISH @ 25123.45 (NSE API (Real-time))

[10:31:00] Market OPEN - Generating prediction...
Fetching data...
✅ Logged: BULLISH @ 25125.30 (NSE API (Real-time))
```

---

### Option 3: Use Both (Best for Month 1)
**Recommended approach:**
1. Run standalone logger for consistent data collection
2. Keep dashboard open for monitoring and visualization

**Setup:**
```bash
# Terminal 1: Dashboard (for monitoring)
streamlit run app.py

# Terminal 2: Standalone logger (for consistent logging)
python standalone_logger.py
```

**Note:** Both will log predictions, but `log_prediction()` handles duplicates gracefully.

---

## Verification

Check logging consistency:
```bash
python check_timing.py
```

Expected output:
```
Average gap: 60 seconds
Expected: 60 seconds (1 minute)
✅ Timing looks good
```

---

## Current Status

**Observed gaps:**
- 10:16:47: 78s gap
- 10:21:01: 254s gap (4+ minutes!)
- 10:21:47: 46s gap
- 10:22:47: 60s gap ✅
- 10:23:50: 63s gap ✅
- 10:26:56: 187s gap (3+ minutes!)

**Average:** 115 seconds (should be 60)

**Cause:** Dashboard tab likely inactive during large gaps

---

## Recommendations for Month 1

### For Reliable Data Collection:
1. **Use standalone logger** - Run `python standalone_logger.py`
2. **Keep it running** - Leave terminal open during market hours
3. **Monitor with dashboard** - Optional, for visualization

### For Monitoring:
1. Check `prediction_log.csv` periodically
2. Run `python check_timing.py` to verify consistency
3. Run `python check_logging_status.py` for quick status

---

## Expected Data Collection Rate

**With consistent 60-second logging:**
- Per hour: 60 predictions
- Per day: ~375 predictions (6.25 hours of market)
- To 300 predictions: ~5 hours (less than 1 day)

**With current inconsistent logging (115s average):**
- Per hour: ~31 predictions
- Per day: ~195 predictions
- To 300 predictions: ~1.5 days

**Impact:** Inconsistent logging will delay reaching 300+ samples for XGBoost training.

---

## Files

- `standalone_logger.py` - Independent prediction logger
- `check_timing.py` - Analyze logging consistency
- `check_logging_status.py` - Quick status check
- `prediction_log.csv` - Data file (accumulates daily)

---

## Troubleshooting

### Standalone logger not logging:
1. Check market hours (9:15 AM - 3:30 PM IST)
2. Check weekday (Monday-Friday only)
3. Check data sources (NSE API or Angel One working)
4. Check API keys in `.env` file

### Dashboard not refreshing:
1. Keep browser tab active and visible
2. Check browser console for errors
3. Restart dashboard: `streamlit run app.py`

### Duplicate predictions:
- Not a problem - `log_prediction()` appends to CSV
- Each prediction has unique timestamp
- Can filter duplicates later if needed

---

## Summary

**Problem:** Inconsistent logging due to Streamlit auto-refresh pausing

**Solution:** Run standalone logger for consistent 60-second intervals

**Command:**
```bash
python standalone_logger.py
```

**Result:** Reliable data collection for XGBoost training (300+ samples in <1 day)

---

**Last Updated:** March 2, 2026

**Status:** Standalone logger created and ready to use
