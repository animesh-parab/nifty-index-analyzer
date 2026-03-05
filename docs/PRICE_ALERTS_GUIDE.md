# 🔔 Price Alerts - User Guide

## Overview

The Price Alerts feature allows you to set target prices for Nifty 50 and get instant browser notifications when those prices are reached.

**No SMS or email required** - notifications appear directly in your browser!

---

## Features

✅ **Browser Notifications** - Instant popup alerts in your browser
✅ **Above/Below Alerts** - Set alerts for price going above or below targets
✅ **Custom Notes** - Add notes to remember why you set each alert
✅ **Alert History** - See recently triggered alerts
✅ **Easy Management** - Add/remove alerts with one click
✅ **Persistent Storage** - Alerts saved even if you close the dashboard
✅ **Real-time Checking** - Alerts checked every 60 seconds with price updates

---

## How to Use

### 1. Open the Sidebar

The sidebar is now visible by default on the left side of the dashboard.

If it's hidden, click the **>** arrow in the top-left corner.

### 2. Add a New Alert

In the sidebar, you'll see the "Add New Alert" section:

1. **Target Price**: Enter the price level (e.g., 25,500)
2. **Alert When**: Choose "above" or "below"
   - **Above**: Alert when price crosses above the target
   - **Below**: Alert when price drops below the target
3. **Note (optional)**: Add a reminder (e.g., "Resistance level")
4. Click **➕ Add Alert**

### 3. View Active Alerts

All your active alerts are shown in the sidebar:

```
⬆️ Above 25,500
   Resistance level
   [🗑️ Delete]

⬇️ Below 25,300
   Support level
   [🗑️ Delete]
```

### 4. Get Notified

When an alert triggers:

1. **Browser Notification** - A popup appears with the alert message
2. **Toast Notification** - A small notification in the dashboard
3. **Warning Banner** - A prominent banner at the top of the dashboard
4. **Sidebar Update** - Alert moves to "Recently Triggered" section

### 5. Manage Alerts

- **Delete Alert**: Click the 🗑️ button next to any alert
- **Clear Triggered**: Click "🗑️ Clear Triggered" to remove old triggered alerts

---

## Examples

### Example 1: Resistance Breakout Alert

**Scenario**: You think Nifty will break above 25,500

**Setup**:
- Target Price: 25,500
- Alert When: above
- Note: "Resistance breakout - consider buying"

**Result**: When Nifty crosses 25,500, you get notified instantly!

### Example 2: Support Level Alert

**Scenario**: You want to know if Nifty drops below support at 25,300

**Setup**:
- Target Price: 25,300
- Alert When: below
- Note: "Support broken - consider selling"

**Result**: When Nifty drops below 25,300, you get notified!

### Example 3: Multiple Alerts

You can set multiple alerts at different levels:

```
⬆️ Above 25,600 - "Strong resistance"
⬆️ Above 25,500 - "First resistance"
⬇️ Below 25,300 - "First support"
⬇️ Below 25,200 - "Strong support"
```

---

## Alert Behavior

### When Alerts Trigger

- **Once Only**: Each alert triggers only once
- **Immediate**: Notification appears within 60 seconds (next refresh)
- **Persistent**: Triggered alerts stay in history until you clear them

### Alert Checking

Alerts are checked:
- Every 60 seconds (when dashboard auto-refreshes)
- Only during market hours (9:15 AM - 3:30 PM IST)
- Using real-time price from Angel One/NSE

### Alert Storage

- Alerts are saved in `price_alerts.json`
- Persists even if you close the dashboard
- Survives browser refresh
- Backed up automatically

---

## Browser Notifications

### Enabling Browser Notifications

For best experience, enable browser notifications:

**Chrome/Edge**:
1. Click the 🔔 icon in the address bar
2. Select "Allow"

**Firefox**:
1. Click the 🔔 icon in the address bar
2. Select "Allow Notifications"

**Safari**:
1. Safari > Preferences > Websites > Notifications
2. Allow notifications for localhost

### Notification Format

```
🔔 PRICE ALERT: Nifty crossed above 25,500
Resistance level
```

---

## Tips & Best Practices

### 1. Set Strategic Levels

Set alerts at:
- Key support/resistance levels
- Round numbers (25,000, 25,500, 26,000)
- Previous day's high/low
- Max Pain level from options chain

### 2. Use Notes Effectively

Good notes help you remember your strategy:
- ✅ "Resistance breakout - consider buying"
- ✅ "Support broken - exit long positions"
- ✅ "Max Pain level - watch for reversal"
- ❌ "Alert 1" (not helpful)

### 3. Don't Set Too Many

- Keep it to 3-5 active alerts
- Too many alerts = alert fatigue
- Focus on key levels only

### 4. Update Regularly

- Remove old alerts that are no longer relevant
- Add new alerts based on current market conditions
- Clear triggered alerts daily

### 5. Combine with AI Predictions

Use alerts with AI predictions:
- If AI predicts BULLISH, set alert above current price
- If AI predicts BEARISH, set alert below current price
- Set alerts at AI's price targets

---

## Troubleshooting

### Alerts Not Triggering

**Problem**: Alert didn't trigger when price reached target

**Solutions**:
1. Check if dashboard is running (not paused)
2. Verify market is open (9:15 AM - 3:30 PM IST)
3. Check if alert was already triggered (moved to "Recently Triggered")
4. Ensure price actually crossed the target (check chart)

### Browser Notifications Not Showing

**Problem**: No popup notification when alert triggers

**Solutions**:
1. Enable browser notifications (see above)
2. Check browser notification settings
3. Ensure dashboard tab is open
4. Try refreshing the page

### Alerts Disappeared

**Problem**: All alerts are gone

**Solutions**:
1. Check `price_alerts.json` file exists
2. Alerts may have been cleared accidentally
3. Re-add alerts (takes 30 seconds)

### Too Many Notifications

**Problem**: Getting too many alerts

**Solutions**:
1. Remove unnecessary alerts
2. Set alerts further from current price
3. Use "Clear Triggered" to clean up

---

## Technical Details

### File Storage

Alerts are stored in `price_alerts.json`:

```json
[
  {
    "id": 1,
    "price": 25500.0,
    "direction": "above",
    "note": "Resistance level",
    "created_at": "2026-02-27T10:30:00+05:30",
    "triggered": false,
    "triggered_at": null
  }
]
```

### Alert Checking Logic

```python
# Check every 60 seconds
current_price = get_live_nifty_price()

for alert in active_alerts:
    if alert['direction'] == 'above':
        if current_price >= alert['price']:
            trigger_alert(alert)
    elif alert['direction'] == 'below':
        if current_price <= alert['price']:
            trigger_alert(alert)
```

### Performance Impact

- **Minimal**: Checking alerts takes <1ms
- **No Extra API Calls**: Uses existing price data
- **Lightweight**: JSON file is <10 KB even with 100 alerts

---

## API & Cost

### API Usage

Price alerts use **ZERO additional API calls**:
- Uses existing price data from dashboard
- No separate API requests
- No impact on rate limits

### Cost

**$0.00** - Completely free!
- No SMS charges
- No email service fees
- No notification service costs
- Browser notifications are free

---

## Future Enhancements

Planned improvements (see FUTURE_IMPROVEMENTS.txt):

1. **Sound Alerts** - Play sound when alert triggers
2. **Voice Alerts** - Text-to-speech announcements
3. **Telegram Integration** - Send alerts to Telegram
4. **Email Alerts** - Optional email notifications
5. **SMS Alerts** - Optional SMS (paid)
6. **Alert Templates** - Pre-configured alert sets
7. **Conditional Alerts** - "Alert if price above X AND RSI > 70"
8. **Time-based Alerts** - "Alert only between 2-3 PM"

---

## Examples in Action

### Day Trading Setup

```
Morning (9:15 AM):
- Set alert above yesterday's high: 25,480
- Set alert below yesterday's low: 25,320

During Day:
- Alert triggers at 25,480 → Consider buying
- Move alert to new resistance: 25,550

End of Day:
- Clear all triggered alerts
- Set new alerts for tomorrow
```

### Swing Trading Setup

```
Weekly:
- Set alert above weekly resistance: 25,800
- Set alert below weekly support: 25,000

When Triggered:
- Analyze chart and indicators
- Check AI prediction
- Make trading decision
```

### Options Trading Setup

```
Based on Options Chain:
- Set alert at Max Pain: 25,400
- Set alert at highest CE OI: 25,500
- Set alert at highest PE OI: 25,300

Use Alerts:
- Price near Max Pain → Expect consolidation
- Price breaks CE OI → Bullish breakout
- Price breaks PE OI → Bearish breakdown
```

---

## FAQ

**Q: How many alerts can I set?**
A: Unlimited! But we recommend 3-5 for best experience.

**Q: Do alerts work when dashboard is closed?**
A: No, dashboard must be open and running.

**Q: Can I set alerts for Bank Nifty?**
A: Not yet, but coming soon! (See FUTURE_IMPROVEMENTS.txt)

**Q: Do alerts work on mobile?**
A: Yes, if you open the dashboard in mobile browser.

**Q: Can I share alerts with friends?**
A: Not yet, but you can manually tell them your alert levels.

**Q: What happens if I set the same alert twice?**
A: Both alerts will trigger independently.

**Q: Can I edit an existing alert?**
A: Not yet - delete and create a new one.

**Q: Do alerts expire?**
A: No, they stay active until triggered or deleted.

---

## Support

If you have issues:

1. Check this guide
2. Run test: `python test_price_alerts.py`
3. Check logs: `logs/2026-02-27/app.log`
4. Restart dashboard: `streamlit run app.py`

---

## Summary

Price Alerts give you:
- ✅ Instant notifications when price reaches your targets
- ✅ No SMS/email required (browser notifications)
- ✅ Easy to set up and manage
- ✅ Completely free ($0.00)
- ✅ Works with existing dashboard

**Start using alerts today to never miss important price levels!**

---

**Last Updated**: February 27, 2026
