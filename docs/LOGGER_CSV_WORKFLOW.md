# Logger & CSV Workflow - Complete Guide

## MORNING (Before 9:15 AM)

### Step 1: Morning Check
- Run `python morning_check.py`
- Verifies time filter is correct
- Checks main CSV status (should have yesterday's data)
- Tests live data fetch
- Tests prediction engine
- Confirms everything ready for market open

### Step 2: Start Logger V2
- Run `python new_logger/standalone_logger_v2.py`
- Logger starts and waits for market open (9:15 AM)
- Creates fresh `predictions_v2.csv` (empty, ready for today)
- Creates fresh `predictions_v2_YYYY_MM_DD.csv` (today's date)

---

## DURING MARKET HOURS (9:15 AM - 3:30 PM)

### Step 3: Logger V2 Runs Every Minute
- Checks if market is open (9:15 - 3:30 PM, Monday-Friday)
- Gets time multiplier for current minute:
  - 9:15-9:30 → None (skip, pre-open volatility)
  - 9:30-10:00 → 0.5x confidence (opening volatile)
  - 10:00-12:00 → 1.0x confidence (prime trading)
  - 12:00-13:30 → 0.6x confidence (lunch)
  - 13:30-14:30 → 1.0x confidence (prime afternoon)
  - 14:30-15:00 → 0.7x confidence (pre-close)
  - 15:00+ → None (skip, post-close - NSE API returns stale data)
- If multiplier is None → skip that minute
- If multiplier exists → fetch data and generate prediction

**Note:** Logger stops collecting at 15:00. The 15:30 market close time is only used for the `is_market_open()` boundary check. No data is collected after 15:00 because NSE API returns stale prices.

### Step 4: Data Collection
- Fetches live Nifty price from NSE API
- Fetches VIX from yfinance
- Calculates all technical indicators (RSI, MACD, EMA, BB, ATR)
- Generates prediction (BULLISH/BEARISH/SIDEWAYS)
- Applies time multiplier to confidence score

### Step 5: Dual CSV Write
- Writes to `new_logger/predictions_v2.csv` (main V2 file)
- Writes to `new_logger/predictions_v2_YYYY_MM_DD.csv` (daily backup)
- Both writes use `QUOTE_ALL` and UTF-8 encoding
- All 17 columns written exactly:
  - timestamp, rsi_14, macd_value, macd_signal
  - ema_9, ema_21, ema_50, bb_position, atr_14
  - vix, day_of_week, us_market_change
  - final_direction, confidence, entry_price
  - data_source, actual_outcome (empty)

### Step 6: Continuous Logging
- Logger runs every 60 seconds
- Expected: ~345 predictions per day (9:15 AM - 3:00 PM = 345 minutes)
- Actual: ~200-250 due to time filter blocking pre-open and post-close periods
- If network fails → logger skips that minute, continues next minute
- If crash → restart logger, continues from current time

---

## AFTER MARKET CLOSE (After 3:00 PM)

### Step 7: Stop Logger
- Press Ctrl+C to stop logger (can stop anytime after 3:00 PM)
- Logger stops cleanly
- Final state:
  - `predictions_v2.csv` has today's data (~200-250 rows)
  - `predictions_v2_YYYY_MM_DD.csv` has identical data (backup)

### Step 8: Run EOD Merge
- Run `python eod_merge.py`
- Script does:
  1. Loads `prediction_log.csv` (main master CSV)
  2. Loads `new_logger/predictions_v2.csv` (today's V2 data)
  3. Verifies both files load cleanly
  4. Checks columns match (17 columns)
  5. Creates backup: `data/backups/prediction_log_before_merge_YYYYMMDD_HHMMSS.csv`
  6. Removes duplicate timestamps (if any)
  7. Merges V2 data into main CSV
  8. Sorts by timestamp
  9. Saves merged CSV
  10. Verifies merged file loads cleanly
  11. **Resets `predictions_v2.csv` to empty** (ready for tomorrow)
  12. **Keeps `predictions_v2_YYYY_MM_DD.csv` untouched** (permanent daily backup)

### Step 9: Verify Merge
- Check main CSV has today's data
- Check row counts match expected
- Check date coverage shows today's date
- If merge failed → restore from backup automatically

---

## FILE STATES AFTER EOD

### Main CSV (`prediction_log.csv`)
- Contains all historical data (March 2, 4, 9, 10...)
- Never written to by logger
- Only updated via `eod_merge.py`
- Always clean and readable

### V2 Live CSV (`new_logger/predictions_v2.csv`)
- Reset to 0 rows (empty, ready for tomorrow)
- Will be populated tomorrow during market hours
- Tracked in Git (shows structure)

### V2 Daily Backup (`new_logger/predictions_v2_YYYY_MM_DD.csv`)
- Contains today's complete data
- Never deleted
- Not tracked in Git (excluded via .gitignore)
- Safety net if merge fails or data needs recovery

### Merge Backup (`data/backups/prediction_log_before_merge_*.csv`)
- Snapshot of main CSV before merge
- Created every EOD
- Allows rollback if merge corrupts data

---

## NEXT MORNING (Repeat)

- Main CSV has all historical data including yesterday
- V2 CSV is empty and ready
- Start logger V2 again
- Cycle repeats

---

## KEY SAFETY FEATURES

1. **Dual Write:** Every prediction written to 2 files simultaneously
2. **Daily Backup:** Permanent copy of each day's data
3. **Merge Backup:** Snapshot before every merge operation
4. **Verification:** Every merge verifies file loads cleanly
5. **Auto Rollback:** If merge fails, restores from backup automatically
6. **No Corruption:** V2 logger uses QUOTE_ALL, UTF-8, clean text
7. **Time Filter:** Skips volatile periods, applies confidence multipliers
8. **Network Resilient:** Skips failed minutes, continues logging

---

## WHAT WE NEVER DO

- ❌ Never write to `prediction_log.csv` during market hours
- ❌ Never delete daily backup files
- ❌ Never merge without creating backup first
- ❌ Never overwrite data without verification
- ❌ Never run logger without morning check
- ❌ Never backfill data after 15:00 (NSE API returns stale prices)
- ❌ Never collect data during 9:15-9:30 (pre-open, no real data)
- ❌ Never collect data after 15:00 (post-close, stale data)

---

## CSV STRUCTURE

### All CSVs have exactly 17 columns:
1. timestamp - ISO format with timezone
2. rsi_14 - RSI indicator value
3. macd_value - MACD line value
4. macd_signal - MACD signal line value
5. ema_9 - 9-period EMA
6. ema_21 - 21-period EMA
7. ema_50 - 50-period EMA
8. bb_position - Bollinger Band position (0-1)
9. atr_14 - Average True Range
10. vix - India VIX value
11. day_of_week - 0=Monday, 4=Friday
12. us_market_change - S&P 500 % change
13. final_direction - BULLISH/BEARISH/SIDEWAYS
14. confidence - 0-100 (after time multiplier applied)
15. entry_price - Nifty price at prediction time
16. data_source - NSE API (Real-time) or Backfilled
17. actual_outcome - Empty (filled later for backtesting)

---

## TIME FILTER DETAILS

The time filter (`get_time_confidence_multiplier()`) controls data collection quality:

| Time Range | Multiplier | Reason |
|------------|-----------|---------|
| Before 9:15 | None | Market closed |
| 9:15-9:30 | None | Pre-open, no real data |
| 9:30-10:00 | 0.5x | Opening volatility |
| 10:00-12:00 | 1.0x | Prime trading hours |
| 12:00-13:30 | 0.6x | Lunch, lower volume |
| 13:30-14:30 | 1.0x | Prime afternoon |
| 14:30-15:00 | 0.7x | Pre-close volatility |
| 15:00+ | None | Post-close, stale data |

**Why skip 15:00-15:30?**
- NSE API continues returning data after 15:00
- But prices are stale (last traded price at 15:00)
- No new trades happening
- Data would be misleading for model training
- Better to stop at 15:00 and have clean data

---

## TROUBLESHOOTING

### Logger crashed during market hours
1. Check last timestamp in `predictions_v2.csv`
2. Restart logger: `python new_logger/standalone_logger_v2.py`
3. Logger continues from current time (no backfill needed)
4. Daily backup file preserves data collected before crash

### Merge failed
1. Check error message in merge output
2. Main CSV automatically restored from backup
3. Fix issue (column mismatch, corruption, etc.)
4. Run `python eod_merge.py` again

### V2 CSV corrupted
1. Daily backup file is untouched: `predictions_v2_YYYY_MM_DD.csv`
2. Copy daily backup to `predictions_v2.csv`
3. Run merge again

### Main CSV corrupted
1. Restore from latest merge backup in `data/backups/`
2. Re-run merge if needed

### Network issues during market hours
- Logger automatically skips failed minutes
- Continues logging when network returns
- Some data loss acceptable (better than corrupted data)
- Daily backup preserves what was collected

---

**Last Updated:** March 9, 2026
**Version:** 2.0 (Logger V2 with dual write and time filter)
