# End of Day Checklist - March 6, 2026

## 🕒 After Market Close (3:30 PM IST)

### Step 1: Stop the Logger
```bash
# The logger will auto-stop at market close, but you can manually stop if needed
# Find the process and stop it
```

**Status**: ⏳ Pending

---

### Step 2: Backfill Missing Outcomes (CRITICAL)
```bash
python scripts/backfill_outcomes.py
```

**What it does**:
- Fills actual outcomes for all predictions from today
- Uses 60-minute lookback with max move logic
- Updates prediction_log.csv with UP/DOWN/SIDEWAYS outcomes

**Expected**:
- ~47 new predictions from 9:30-10:16 backfill need outcomes
- Plus any predictions logged after 10:20 AM
- Total: ~100-150 predictions to backfill

**Status**: ⏳ Pending

---

### Step 3: Generate End of Day Report
```bash
python scripts/end_of_day_report.py
```

**What it does**:
- Shows total predictions collected today
- Shows predictions with outcomes
- Shows accuracy statistics
- Shows data quality metrics

**Status**: ⏳ Pending

---

### Step 4: Check System Status
```bash
python scripts/check_current_status.py
```

**What it does**:
- Verifies all predictions have outcomes
- Checks for duplicates
- Validates data quality
- Shows readiness for XGBoost training

**Status**: ⏳ Pending

---

### Step 5: Backup Today's Data
```bash
# Create backup with today's date
python -c "import pandas as pd; from datetime import datetime; df = pd.read_csv('prediction_log.csv'); df.to_csv(f'backups/prediction_log_backup_{datetime.now().strftime(\"%Y%m%d_%H%M%S\")}.csv', index=False); print('Backup created')"
```

**What it does**:
- Creates timestamped backup in backups/ folder
- Protects against data loss
- Allows rollback if needed

**Status**: ⏳ Pending

---

### Step 6: Check Prediction Log Stats
```bash
python -c "import pandas as pd; df = pd.read_csv('prediction_log.csv'); print(f'Total predictions: {len(df)}'); print(f'With outcomes: {df[\"actual_outcome\"].notna().sum()}'); print(f'Missing outcomes: {df[\"actual_outcome\"].isna().sum()}'); print(f'Ready for training: {df[\"actual_outcome\"].notna().sum() >= 300}')"
```

**Expected Output**:
```
Total predictions: ~700-750
With outcomes: ~650-700
Missing outcomes: 0-50 (recent predictions only)
Ready for training: True
```

**Status**: ⏳ Pending

---

### Step 7: Review Trade Signals (Optional)
```bash
# Check trade_journal.md for any signals that fired today
# Review if any CALL/PUT setups were detected
# Document performance if trades were taken
```

**What to check**:
- How many CALL signals fired?
- How many PUT signals fired?
- Were confluence requirements met (7/7)?
- Did any signals meet entry criteria?

**Status**: ⏳ Pending

---

### Step 8: Clean Up Temporary Files (Optional)
```bash
# Remove any temporary files created during the day
Remove-Item *.tmp -ErrorAction SilentlyContinue
Remove-Item prediction_log_fixed.csv -ErrorAction SilentlyContinue
```

**Status**: ⏳ Pending

---

### Step 9: Commit and Push to GitHub
```bash
git add prediction_log.csv
git add backups/
git commit -m "EOD: March 6, 2026 - Added [X] predictions with outcomes"
git push origin main
```

**Note**: Only push if you want to backup prediction data to GitHub. The .gitignore blocks *.csv by default except instruments_nifty_options.csv.

**Status**: ⏳ Pending

---

### Step 10: Plan for Tomorrow
```bash
# Review what worked today
# Check if any adjustments needed
# Ensure logger will start automatically tomorrow at 9:15 AM
```

**Tomorrow's Plan**:
- [ ] Start logger at 9:15 AM: `python standalone_logger.py`
- [ ] Monitor dashboard: `streamlit run app.py`
- [ ] Watch for trade signals during 10:00-12:00 and 1:30-2:30
- [ ] Continue data collection for XGBoost training

**Status**: ⏳ Pending

---

## 📊 Today's Summary (To be filled after Step 3)

**Data Collection**:
- Predictions logged: ___
- With outcomes: ___
- Data quality: ___

**Trade Signals**:
- CALL signals: ___
- PUT signals: ___
- Signals taken: ___

**System Health**:
- API errors: ___
- Data source: NSE / Angel One / Both
- Logger uptime: ___

---

## 🚨 Issues to Address (If Any)

- [ ] None yet

---

## 📝 Notes

- CSV was corrupted earlier today (line 620 error) - fixed by skipping bad lines
- Backfilled 47 predictions from 9:30-10:16 AM
- Logger started at 10:20 AM
- Options chain API having issues (Angel One returning empty responses)

---

**Created**: March 6, 2026 10:22 AM IST
**Last Updated**: March 6, 2026 10:22 AM IST
**Status**: In Progress - Market Open
