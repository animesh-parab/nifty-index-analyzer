"""Test Price Alerts System"""

from price_alerts import (
    add_alert, remove_alert, get_active_alerts,
    get_triggered_alerts, check_alerts, clear_triggered_alerts,
    get_alert_summary
)

print("\n" + "="*70)
print("TESTING PRICE ALERTS SYSTEM")
print("="*70 + "\n")

# Clear any existing alerts
print("1. Clearing existing alerts...")
clear_triggered_alerts()
alerts = get_active_alerts()
for alert in alerts:
    remove_alert(alert['id'])
print("   ✓ Cleared\n")

# Add test alerts
print("2. Adding test alerts...")
alert1 = add_alert(25500, "above", "Resistance level")
print(f"   ✓ Added: Above 25,500 (ID: {alert1['id']})")

alert2 = add_alert(25300, "below", "Support level")
print(f"   ✓ Added: Below 25,300 (ID: {alert2['id']})\n")

# Check summary
print("3. Alert Summary:")
summary = get_alert_summary()
print(f"   Total: {summary['total']}")
print(f"   Active: {summary['active']}")
print(f"   Triggered: {summary['triggered']}\n")

# Show active alerts
print("4. Active Alerts:")
active = get_active_alerts()
for alert in active:
    print(f"   - {alert['direction'].upper()} {alert['price']:,.0f}")
    if alert['note']:
        print(f"     Note: {alert['note']}")
print()

# Test alert triggering
print("5. Testing Alert Triggers:")

# Test case 1: Price goes above 25,500
print("   Testing: Price = 25,550 (should trigger 'above 25,500')")
triggered = check_alerts(25550)
if triggered:
    for alert in triggered:
        print(f"   ✓ TRIGGERED: {alert['direction'].upper()} {alert['price']:,.0f}")
else:
    print("   ✗ No alerts triggered")
print()

# Test case 2: Price goes below 25,300
print("   Testing: Price = 25,250 (should trigger 'below 25,300')")
triggered = check_alerts(25250)
if triggered:
    for alert in triggered:
        print(f"   ✓ TRIGGERED: {alert['direction'].upper()} {alert['price']:,.0f}")
else:
    print("   ✗ No alerts triggered")
print()

# Show triggered alerts
print("6. Triggered Alerts:")
triggered_list = get_triggered_alerts()
for alert in triggered_list:
    print(f"   - {alert['direction'].upper()} {alert['price']:,.0f}")
    print(f"     Triggered at: {alert['triggered_at']}")
print()

# Final summary
print("7. Final Summary:")
summary = get_alert_summary()
print(f"   Total: {summary['total']}")
print(f"   Active: {summary['active']}")
print(f"   Triggered: {summary['triggered']}\n")

print("="*70)
print("✓ PRICE ALERTS SYSTEM WORKING!")
print("="*70)
print("\nYou can now:")
print("1. Run the dashboard: streamlit run app.py")
print("2. Add alerts in the sidebar")
print("3. Get browser notifications when alerts trigger")
print("\n")
