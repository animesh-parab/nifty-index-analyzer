# Data Availability Guide

## What Data is Available When?

This guide explains which data sources are available during market hours vs. outside market hours.

---

## ✅ ALWAYS AVAILABLE (24/7)

These data sources work anytime, even when market is closed:

### 1. Nifty Price
- **Sources:** NSE API → Angel One → yfinance
- **Availability:** 24/7
- **Note:** Outside market hours, shows last closing price
- **Delay:** Real-time during market hours, delayed outside

### 2. India VIX
- **Source:** yfinance
- **Availability:** 24/7
- **Note:** Shows last available VIX value
- **Delay:** ~15 minutes

### 3. Technical Indicators
- **Calculated from:** Historical candle data
- **Availability:** 24/7
- **Includes:**
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - EMA (Exponential Moving Averages)
  - Bollinger Bands
  - ATR (Average True Range)
  - Candlestick patterns

### 4. Global Market Cues
- **Sources:** yfinance (US markets)
- **Availability:** 24/7
- **Includes:**
  - Dow Jones
  - S&P 500
  - Nasdaq
  - Nikkei
  - Hang Seng
- **Note:** Shows last closing values outside trading hours

### 5. News
- **Sources:** RSS feeds (ET, MoneyControl, LiveMint, BS)
- **Availability:** 24/7
- **Updates:** Scheduled at 9 AM, 12 PM, 3 PM IST

---

## ⏰ MARKET HOURS ONLY (9:15 AM - 3:30 PM IST)

These data sources ONLY work during market hours:

### 1. Options Chain Data
- **Sources:** Angel One → NSE API
- **Availability:** ONLY during market hours
- **Reason:** Options data is not published outside trading hours
- **Includes:**
  - Call/Put Open Interest (OI)
  - Strike prices
  - Option premiums
  - Greeks (Delta, Gamma, Theta, Vega)

### 2. PCR (Put-Call Ratio)
- **Calculated from:** Options chain data
- **Availability:** ONLY during market hours
- **Display when closed:** "N/A - Market Closed"
- **Updates:** Every 5 minutes (rate limit optimization)

### 3. Max Pain
- **Calculated from:** Options chain data
- **Availability:** ONLY during market hours
- **Display when closed:** "N/A - Market Closed"
- **Updates:** Every 5 minutes

### 4. Open Interest Analysis
- **Source:** Options chain data
- **Availability:** ONLY during market hours
- **Display when closed:** "🔴 Market Closed" message
- **Includes:**
  - OI chart (CE vs PE)
  - Support levels (PE OI)
  - Resistance levels (CE OI)

### 5. Real-time Price Updates
- **Sources:** NSE API → Angel One
- **Availability:** ONLY during market hours
- **Outside hours:** Falls back to yfinance (delayed)
- **Note:** Price still shows, but may be delayed

---

## Dashboard Display Behavior

### During Market Hours (9:15 AM - 3:30 PM IST)

**All data available:**
```
✅ Nifty Price (real-time)
✅ VIX (real-time)
✅ PCR (live, updates every 5 min)
✅ Max Pain (live, updates every 5 min)
✅ Open Interest Chart (live)
✅ Technical Indicators (live)
✅ AI Predictions (live)
✅ Logging: ACTIVE ✅
```

**Banner shows:**
```
┌────────────────────────────────────────────────────────┐
│ ✅ REAL-TIME DATA ACTIVE • NSE API • Live Market Data │
│                                          ✅ LOGGING    │
└────────────────────────────────────────────────────────┘
```

### Outside Market Hours (3:30 PM - 9:15 AM IST)

**Limited data:**
```
✅ Nifty Price (last closing price)
✅ VIX (last available value)
❌ PCR → Shows "N/A - Market Closed"
❌ Max Pain → Shows "N/A - Market Closed"
❌ Open Interest → Shows "🔴 Market Closed" message
✅ Technical Indicators (from historical data)
✅ AI Predictions (based on available data)
❌ Logging: PAUSED ⏸
```

**Banner shows:**
```
┌────────────────────────────────────────────────────────┐
│ ✅ REAL-TIME DATA ACTIVE • NSE API • Live Market Data │
│                                          ⏸ PAUSED      │
└────────────────────────────────────────────────────────┘
```

---

## Why Options Data is Not Available Outside Market Hours

### Technical Reason:
- Options exchanges (NSE, BSE) only publish live options data during trading hours
- Angel One API returns empty responses for options outside market hours
- NSE website doesn't show options chain when market is closed
- This is by design - options data is only meaningful during active trading

### What Happens:
1. Dashboard tries to fetch options chain
2. Angel One returns empty response (no error, just no data)
3. NSE fallback also returns empty
4. Dashboard shows "Market Closed" message instead of "0.000" or errors

### When It Resumes:
- Automatically at 9:15 AM IST when market opens
- No manual intervention needed
- Dashboard will start showing live PCR, Max Pain, and OI data

---

## Data Source Priority

### Nifty Price:
```
1. NSE API (Primary) → Real-time, 0 delay
   ↓ (if fails)
2. Angel One (Backup) → Real-time, 0 delay
   ↓ (if fails)
3. yfinance (Fallback) → 15 min delay
```

### Options Chain:
```
1. Angel One (Primary) → Real-time, 0 delay
   ↓ (if fails)
2. NSE API (Backup) → Real-time, 0 delay
   ↓ (if fails)
3. Return empty → Show "Market Closed" message
```

### VIX:
```
1. yfinance (Only source) → ~15 min delay
   Note: Angel One VIX token is incorrect, so we use yfinance
```

---

## Prediction Logging Behavior

### When Predictions are Logged:

**Requirements (ALL must be true):**
1. ✅ Market is open (9:15 AM - 3:30 PM IST)
2. ✅ Using real-time data (NSE or Angel One)
3. ✅ Dashboard is running
4. ✅ Valid prediction generated

**Result:** Prediction logged to `prediction_log.csv`

### When Predictions are NOT Logged:

**Scenario 1: Market Closed**
- Time: Outside 9:15 AM - 3:30 PM IST
- Data source: NSE or Angel One (real-time)
- Banner: "⏸ PAUSED"
- Reason: No point logging when market is closed

**Scenario 2: Using Delayed Data**
- Time: During market hours
- Data source: yfinance (15 min delay)
- Banner: "🚫 NOT LOGGING"
- Reason: Delayed data would corrupt training set

**Scenario 3: Dashboard Not Running**
- Dashboard: Stopped
- Result: No predictions, no logging

---

## Common Questions

### Q: Why does PCR show "N/A" at night?
**A:** Options data is only available during market hours (9:15 AM - 3:30 PM IST). This is normal behavior.

### Q: Will PCR data appear automatically when market opens?
**A:** Yes! At 9:15 AM, the dashboard will automatically fetch options chain data and PCR will update.

### Q: Why does Nifty price still show outside market hours?
**A:** Price data shows the last closing price. It's not live, but it's still useful for reference.

### Q: Can I collect prediction data outside market hours?
**A:** No. Predictions are only logged during market hours when using real-time data. This ensures training data quality.

### Q: What if I run the dashboard 24/7?
**A:** Perfect! The dashboard will:
- Show available data 24/7
- Automatically start logging at 9:15 AM
- Automatically pause logging at 3:30 PM
- Resume next day at 9:15 AM

### Q: Do I need to restart the dashboard when market opens?
**A:** No! The dashboard automatically detects market hours and starts/stops logging accordingly.

---

## Summary Table

| Data Type | Market Hours | Outside Hours | Source |
|-----------|-------------|---------------|--------|
| Nifty Price | ✅ Real-time | ✅ Last close | NSE/Angel One/yfinance |
| VIX | ✅ Real-time | ✅ Last value | yfinance |
| PCR | ✅ Live | ❌ N/A | Options chain |
| Max Pain | ✅ Live | ❌ N/A | Options chain |
| Open Interest | ✅ Live | ❌ N/A | Options chain |
| Technical Indicators | ✅ Live | ✅ Historical | Calculated |
| Global Cues | ✅ Live | ✅ Last close | yfinance |
| News | ✅ Live | ✅ Cached | RSS feeds |
| Predictions | ✅ Logged | ⏸ Paused | AI models |

---

## Best Practices

### 1. Run Dashboard 24/7
- Let it run continuously
- Automatic start/stop of logging
- No manual intervention needed

### 2. Check Banner Status
- "✅ LOGGING" = Data being collected
- "⏸ PAUSED" = Market closed, normal
- "🚫 NOT LOGGING" = Problem, check data source

### 3. Verify Data Collection
```bash
# Check if predictions are being logged
python quick_verify_logger.py

# Should show new rows during market hours
```

### 4. Don't Worry About N/A Values
- PCR = N/A outside market hours → Normal
- Max Pain = N/A outside market hours → Normal
- Open Interest = Market Closed → Normal

### 5. Monitor During Market Hours
- Check dashboard at 9:15 AM
- Verify "✅ LOGGING" status
- Confirm PCR and OI data appear
- Let it run until 3:30 PM

---

## Troubleshooting

### Problem: PCR shows N/A during market hours

**Check:**
1. Is market actually open? (9:15 AM - 3:30 PM IST)
2. Check terminal for Angel One errors
3. Verify Angel One credentials in `.env`
4. Check NSE website - is options chain available?

**Fix:**
- Wait 5 minutes (rate limit)
- Refresh dashboard
- Check Angel One API status

### Problem: Open Interest chart not showing

**Same as PCR** - options data issue. Follow steps above.

### Problem: All data shows N/A

**Check:**
1. Internet connection
2. Dashboard is running
3. Check terminal for errors

---

## Conclusion

**Normal Behavior:**
- ✅ PCR/Max Pain/OI = N/A outside market hours
- ✅ Logging paused outside market hours
- ✅ Price/VIX/Indicators available 24/7

**Automatic Behavior:**
- ✅ Dashboard detects market hours
- ✅ Starts logging at 9:15 AM
- ✅ Stops logging at 3:30 PM
- ✅ No manual intervention needed

**Your Action:**
- ✅ Keep dashboard running
- ✅ Check banner status
- ✅ Verify logging during market hours
- ✅ Let it collect data for 10-20 days

Everything is working as designed! 🎯
