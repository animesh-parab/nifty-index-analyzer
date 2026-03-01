"""
price_alerts.py
Price Alert System with Browser Notifications
"""

import json
import os
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

ALERTS_FILE = "price_alerts.json"


def load_alerts():
    """Load alerts from JSON file"""
    if os.path.exists(ALERTS_FILE):
        try:
            with open(ALERTS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []


def save_alerts(alerts):
    """Save alerts to JSON file"""
    with open(ALERTS_FILE, 'w') as f:
        json.dump(alerts, f, indent=2)


def add_alert(price, direction, note=""):
    """
    Add a new price alert
    
    Args:
        price: Target price
        direction: 'above' or 'below'
        note: Optional note for the alert
    """
    alerts = load_alerts()
    
    alert = {
        "id": len(alerts) + 1,
        "price": float(price),
        "direction": direction,
        "note": note,
        "created_at": datetime.now(IST).isoformat(),
        "triggered": False,
        "triggered_at": None
    }
    
    alerts.append(alert)
    save_alerts(alerts)
    return alert


def remove_alert(alert_id):
    """Remove an alert by ID"""
    alerts = load_alerts()
    alerts = [a for a in alerts if a['id'] != alert_id]
    save_alerts(alerts)


def clear_triggered_alerts():
    """Remove all triggered alerts"""
    alerts = load_alerts()
    alerts = [a for a in alerts if not a['triggered']]
    save_alerts(alerts)


def check_alerts(current_price):
    """
    Check if any alerts should be triggered
    
    Args:
        current_price: Current Nifty price
        
    Returns:
        List of triggered alerts
    """
    alerts = load_alerts()
    triggered = []
    
    for alert in alerts:
        if alert['triggered']:
            continue
            
        target_price = alert['price']
        direction = alert['direction']
        
        # Check if alert condition is met
        if direction == 'above' and current_price >= target_price:
            alert['triggered'] = True
            alert['triggered_at'] = datetime.now(IST).isoformat()
            triggered.append(alert)
        elif direction == 'below' and current_price <= target_price:
            alert['triggered'] = True
            alert['triggered_at'] = datetime.now(IST).isoformat()
            triggered.append(alert)
    
    # Save updated alerts
    if triggered:
        save_alerts(alerts)
    
    return triggered


def get_active_alerts():
    """Get all active (non-triggered) alerts"""
    alerts = load_alerts()
    return [a for a in alerts if not a['triggered']]


def get_triggered_alerts():
    """Get all triggered alerts"""
    alerts = load_alerts()
    return [a for a in alerts if a['triggered']]


def get_alert_summary():
    """Get summary of alerts"""
    alerts = load_alerts()
    active = [a for a in alerts if not a['triggered']]
    triggered = [a for a in alerts if a['triggered']]
    
    return {
        "total": len(alerts),
        "active": len(active),
        "triggered": len(triggered)
    }
