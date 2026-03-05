# 📊 API Rate Limit Monitoring - User Guide

## Overview

The API Rate Limit Monitoring feature tracks your API usage in real-time and alerts you when approaching limits. This ensures you never hit rate limits and helps optimize API usage.

**100% automatic** - no configuration needed!

---

## Features

✅ **Real-time Tracking** - Monitor all API calls as they happen
✅ **Usage Statistics** - See hourly and daily usage for each API
✅ **Status Indicators** - Visual OK/WARNING/CRITICAL status
✅ **Smart Alerts** - Get notified before hitting limits
✅ **Usage Projection** - Estimate end-of-day usage
✅ **Token Tracking** - Track AI API token consumption
✅ **Zero Cost** - No additional API calls or fees

---

## How It Works

### Automatic Tracking

Every API call is automatically recorded:
- **Groq AI** - Chat completions + token count
- **Gemini AI** - Content generation
- **Angel One** - Market data requests
- **NSE API** - Nifty price and options data
- **yfinance** - Fallback data requests

### Status Levels

🟢 **OK** - Usage below 80% of limit
🟡 **WARNING** - Usage between 80-95% of limit
🔴 **CRITICAL** - Usage above 95% of limit

### Rate Limits

| API | Daily Limit | Hourly Limit |
|-----|-------------|--------------|
| Groq AI | 14,400 | 900 |
| Gemini AI | 1,500 | 100 |
| Angel One | 120,000 | 5,000 |
| NSE API | 10,000* | 500* |
| yfinance | Unlimited | Unlimited |

*Estimated limits

---

## Using the Monitor

### 1. View in Sidebar

Open the dashboard sidebar (left side) and scroll to:

**📊 API Usage Monitor**

### 2. Check Overall Status

At the top, you'll see:
- ✅ "All APIs OK" - Everything is fine
- ⚠️ "X API(s) approaching limits" - Warning
- 🚨 "X API(s) at critical usage" - Take action!

### 3. View Detailed Stats

Click **"📈 Detailed Usage Stats"** to expand:

For each API, you'll see:
- **Status** (🟢/🟡/🔴)
- **Today's usage** (calls + percentage)
- **Limit** (total + remaining)
- **Progress bar** (visual usage)

Example:
```
🟢 Groq AI
Today: 375 (2.6%)
Limit: 14,400 (14,025 left)
[▓░░░░░░░░░] 375 / 14,400
```

### 4. Check Projections

Click **"🔮 Estimated Daily Usage"** to see:

Based on current usage rate, estimated end-of-day usage:

```
Groq AI 🟢 OK
Current: 100 → Estimated: 375 / 14,400 (2.6%)
```

This helps you plan ahead!

---

## Understanding Alerts

### Warning Alert (🟡)

**When**: Usage reaches 80% of limit

**Example**:
```
⚠️ Gemini AI usage at 82.5% of daily limit
```

**Action**: 
- Monitor usage
- Consider reducing refresh rate
- Switch to fallback if available

### Critical Alert (🔴)

**When**: Usage reaches 95% of limit

**Example**:
```
🚨 Gemini AI usage at 96.2% of daily limit!
```

**Action**:
- Stop non-essential API calls
- Use fallback sources
- Wait for limit reset (next day)

---

## Usage Scenarios

### Normal Day (All OK)

```
📊 API Usage Monitor
✅ All APIs OK - 6,237 calls today

📈 Detailed Usage Stats
🟢 Groq AI: 375 / 14,400 (2.6%)
🟢 Gemini AI: 375 / 1,500 (25%)
🟢 Angel One: 5,025 / 120,000 (4.2%)
🟢 NSE API: 180 / 10,000 (1.8%)
🟢 yfinance: 450 / ∞ (0%)
```

**Status**: Everything is fine! ✅

### Warning Scenario

```
📊 API Usage Monitor
⚠️ 1 API(s) approaching limits

⚠️ Gemini AI usage at 85% of daily limit

📈 Detailed Usage Stats
🟢 Groq AI: 375 / 14,400 (2.6%)
🟡 Gemini AI: 1,275 / 1,500 (85%)
🟢 Angel One: 5,025 / 120,000 (4.2%)
```

**Status**: Watch Gemini usage ⚠️

### Critical Scenario

```
📊 API Usage Monitor
🚨 1 API(s) at critical usage!

🚨 Gemini AI usage at 96.5% of daily limit!

📈 Detailed Usage Stats
🟢 Groq AI: 375 / 14,400 (2.6%)
🔴 Gemini AI: 1,448 / 1,500 (96.5%)
🟢 Angel One: 5,025 / 120,000 (4.2%)
```

**Status**: Gemini almost at limit! 🚨

---

## What Happens When You Hit a Limit?

### Groq AI Limit

**Impact**: AI predictions will fail
**Fallback**: System uses Gemini only
**Recovery**: Limit resets at midnight UTC

### Gemini AI Limit

**Impact**: AI predictions will fail
**Fallback**: System uses Groq only
**Recovery**: Limit resets at midnight UTC

### Both AI Limits

**Impact**: No AI predictions
**Fallback**: Rule-based predictions (technical indicators)
**Recovery**: Wait for limit reset

### Angel One Limit

**Impact**: No real-time data from Angel One
**Fallback**: NSE API → yfinance (15-min delay)
**Recovery**: Limit resets at midnight IST

### NSE API Limit

**Impact**: No real-time data from NSE
**Fallback**: Angel One → yfinance
**Recovery**: Limit resets hourly

---

## Optimization Tips

### 1. Monitor During Market Hours

Check the monitor at:
- **10:00 AM** - After 45 minutes of trading
- **12:00 PM** - Mid-day check
- **3:00 PM** - Before market close

### 2. Use Projections

If projected usage shows you'll hit limits:
- Reduce dashboard refresh rate
- Pause dashboard when not watching
- Use fallback sources

### 3. Prioritize APIs

If approaching limits:
1. **Keep**: Angel One (real-time data)
2. **Keep**: Groq AI (better predictions)
3. **Reduce**: Gemini AI (Groq is enough)
4. **Reduce**: NSE API (Angel One is better)

### 4. Reset Daily

Usage resets automatically:
- **AI APIs**: Midnight UTC
- **Angel One**: Midnight IST
- **NSE**: Hourly

---

## Technical Details

### Data Storage

Usage data stored in `api_usage.json`:

```json
{
  "groq": {
    "calls": [
      {
        "timestamp": "2026-02-27T10:30:00+05:30",
        "endpoint": "chat.completions",
        "tokens": 500
      }
    ],
    "total": 375
  }
}
```

### Automatic Cleanup

- Old data (>24 hours) automatically removed
- Keeps file size small (<100 KB)
- No manual cleanup needed

### Performance Impact

- **Tracking overhead**: <1ms per API call
- **Storage**: <100 KB disk space
- **Memory**: <1 MB RAM
- **No extra API calls**: Uses existing data

---

## Troubleshooting

### Monitor Shows 0 Usage

**Problem**: All APIs show 0 calls

**Solutions**:
1. Dashboard just started (wait 60 seconds)
2. Check if `api_usage.json` exists
3. Restart dashboard

### Incorrect Usage Numbers

**Problem**: Numbers don't match actual usage

**Solutions**:
1. Check system time (must be correct)
2. Delete `api_usage.json` and restart
3. Old data may be cached (wait 60 seconds)

### Alerts Not Showing

**Problem**: No alerts even when approaching limits

**Solutions**:
1. Check thresholds in `api_rate_monitor.py`
2. Verify usage is actually high
3. Restart dashboard

---

## API Limits Reference

### Groq AI

- **Free Tier**: 14,400 requests/day
- **Rate**: 30 requests/minute
- **Tokens**: 6,000 tokens/minute
- **Reset**: Midnight UTC
- **Upgrade**: $0.59 per million tokens

### Gemini AI

- **Free Tier**: 1,500 requests/day
- **Rate**: 15 requests/minute
- **Tokens**: 1 million tokens/day
- **Reset**: Midnight UTC
- **Upgrade**: $0.35 per million tokens

### Angel One

- **Free Tier**: 120,000 requests/day (estimated)
- **Rate**: 5,000 requests/hour
- **Reset**: Midnight IST
- **Cost**: Free forever

### NSE API

- **Unofficial**: No official limits
- **Estimated**: 10,000 requests/day
- **Rate**: 500 requests/hour
- **Reset**: Hourly
- **Cost**: Free

### yfinance

- **Limits**: None (community API)
- **Rate**: Unlimited
- **Cost**: Free
- **Note**: 15-minute delayed data

---

## Cost Impact

### Monitoring Cost

**$0.00** - Completely free!

- No additional API calls
- No external services
- No subscription fees
- Pure Python tracking

### Optimization Savings

By avoiding rate limits:
- **Save time**: No downtime
- **Save money**: No need to upgrade
- **Peace of mind**: Always know your usage

---

## Future Enhancements

Planned improvements:

1. **Email Alerts** - Get notified via email
2. **Historical Charts** - View usage trends
3. **Export Reports** - Download usage reports
4. **Custom Thresholds** - Set your own warning levels
5. **API Cost Tracking** - Track costs if you upgrade
6. **Webhook Alerts** - Send to Slack/Discord
7. **Usage Recommendations** - AI-powered optimization tips

---

## FAQ

**Q: Does monitoring use extra API calls?**
A: No! It tracks existing calls with zero overhead.

**Q: What happens if I hit a limit?**
A: Dashboard automatically falls back to alternative sources.

**Q: Can I reset usage manually?**
A: Yes, delete `api_usage.json` or use `reset_usage()` function.

**Q: How accurate are the projections?**
A: Very accurate during market hours. Based on current usage rate.

**Q: Do I need to configure anything?**
A: No! Monitoring is automatic and always on.

**Q: Can I disable monitoring?**
A: Yes, but not recommended. It has zero performance impact.

**Q: What if I want higher limits?**
A: You can upgrade to paid tiers (see API Limits Reference).

---

## Summary

API Rate Limit Monitoring gives you:
- ✅ Real-time usage tracking
- ✅ Smart alerts before hitting limits
- ✅ Usage projections
- ✅ Zero cost and zero overhead
- ✅ Peace of mind

**Never worry about rate limits again!**

---

**Last Updated**: February 27, 2026
