# Start Standalone Logger

## The standalone logger is ready to run!

### To start it manually:

Open a terminal/command prompt and run:

```bash
python standalone_logger.py
```

### What it will do:

1. Check if market is open (9:15 AM - 3:30 PM IST, Mon-Fri)
2. If market is open: Generate and log predictions every 60 seconds
3. If market is closed: Wait and check every 60 seconds
4. Write to `prediction_log.csv` automatically
5. Fill outcomes after 15 minutes for each prediction

### You'll see output like:

```
======================================================================
STANDALONE PREDICTION LOGGER
======================================================================
This will log predictions every 60 seconds during market hours
Press Ctrl+C to stop
======================================================================

[11:22:00] Market OPEN - Generating prediction...
INFO:standalone_logger:Fetching data...
INFO:standalone_logger:✅ Logged: BEARISH @ 24823.2 (NSE API Real-time)

[11:23:00] Market OPEN - Generating prediction...
INFO:standalone_logger:Fetching data...
INFO:standalone_logger:✅ Logged: BEARISH @ 24820.5 (NSE API Real-time)
```

### To stop it:

Press `Ctrl+C` in the terminal

### To check if it's working:

Open another terminal and run:
```bash
python verify_all_fixes.py
```

Or check the CSV file directly:
```bash
# View last 5 predictions
python -c "import pandas as pd; df = pd.read_csv('prediction_log.csv'); print(df.tail(5))"
```

### Current Status:

✅ Schedule library installed
✅ PCR column removed
✅ Outcomes backfilled
✅ Exact 60-second intervals configured
✅ Ready to collect data!

---

**Note:** The logger needs to run during market hours (9:15 AM - 3:30 PM IST) to collect data. Outside market hours, it will just wait and check every 60 seconds.

**Tip:** Run this in a separate terminal window and leave it running all day during market hours to collect maximum data for XGBoost training!
