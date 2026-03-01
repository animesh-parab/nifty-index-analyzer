"""
api_rate_monitor.py
API Rate Limit Monitoring System
Tracks API usage and alerts when approaching limits
"""

import json
import os
from datetime import datetime, timedelta
import pytz

IST = pytz.timezone("Asia/Kolkata")

USAGE_FILE = "api_usage.json"

# API Rate Limits (per day)
RATE_LIMITS = {
    "groq": {
        "daily_limit": 14400,
        "hourly_limit": 900,
        "name": "Groq AI",
        "warning_threshold": 0.8,  # 80%
        "critical_threshold": 0.95  # 95%
    },
    "gemini": {
        "daily_limit": 1500,
        "hourly_limit": 100,
        "name": "Gemini AI",
        "warning_threshold": 0.8,
        "critical_threshold": 0.95
    },
    "angel_one": {
        "daily_limit": 120000,
        "hourly_limit": 5000,
        "name": "Angel One",
        "warning_threshold": 0.8,
        "critical_threshold": 0.95
    },
    "nse": {
        "daily_limit": 10000,  # Estimated
        "hourly_limit": 500,   # Estimated
        "name": "NSE API",
        "warning_threshold": 0.8,
        "critical_threshold": 0.95
    },
    "yfinance": {
        "daily_limit": 999999,  # Unlimited
        "hourly_limit": 999999,
        "name": "yfinance",
        "warning_threshold": 0.8,
        "critical_threshold": 0.95
    }
}


def load_usage():
    """Load API usage from JSON file"""
    if os.path.exists(USAGE_FILE):
        try:
            with open(USAGE_FILE, 'r') as f:
                data = json.load(f)
                # Clean old data (older than 24 hours)
                now = datetime.now(IST)
                cutoff = now - timedelta(hours=24)
                
                for api in data:
                    if 'calls' in data[api]:
                        data[api]['calls'] = [
                            call for call in data[api]['calls']
                            if datetime.fromisoformat(call['timestamp']) > cutoff
                        ]
                return data
        except:
            return _init_usage()
    return _init_usage()


def _init_usage():
    """Initialize usage tracking"""
    return {
        "groq": {"calls": [], "total": 0},
        "gemini": {"calls": [], "total": 0},
        "angel_one": {"calls": [], "total": 0},
        "nse": {"calls": [], "total": 0},
        "yfinance": {"calls": [], "total": 0}
    }


def save_usage(usage):
    """Save API usage to JSON file"""
    with open(USAGE_FILE, 'w') as f:
        json.dump(usage, f, indent=2)


def record_api_call(api_name, endpoint="", tokens=0):
    """
    Record an API call
    
    Args:
        api_name: Name of API (groq, gemini, angel_one, nse, yfinance)
        endpoint: Optional endpoint name
        tokens: Optional token count (for AI APIs)
    """
    usage = load_usage()
    
    if api_name not in usage:
        usage[api_name] = {"calls": [], "total": 0}
    
    call = {
        "timestamp": datetime.now(IST).isoformat(),
        "endpoint": endpoint,
        "tokens": tokens
    }
    
    usage[api_name]["calls"].append(call)
    usage[api_name]["total"] += 1
    
    save_usage(usage)


def get_usage_stats(api_name):
    """
    Get usage statistics for an API
    
    Returns:
        dict with hourly and daily usage, percentages, and status
    """
    usage = load_usage()
    
    if api_name not in usage or api_name not in RATE_LIMITS:
        return None
    
    now = datetime.now(IST)
    hour_ago = now - timedelta(hours=1)
    
    calls = usage[api_name]["calls"]
    
    # Count calls in last hour
    hourly_calls = len([
        c for c in calls
        if datetime.fromisoformat(c['timestamp']) > hour_ago
    ])
    
    # Count calls in last 24 hours (all calls since we clean old ones)
    daily_calls = len(calls)
    
    # Get limits
    limits = RATE_LIMITS[api_name]
    
    # Calculate percentages
    hourly_pct = (hourly_calls / limits['hourly_limit']) * 100 if limits['hourly_limit'] > 0 else 0
    daily_pct = (daily_calls / limits['daily_limit']) * 100 if limits['daily_limit'] > 0 else 0
    
    # Determine status
    max_pct = max(hourly_pct, daily_pct)
    if max_pct >= limits['critical_threshold'] * 100:
        status = "CRITICAL"
        color = "red"
    elif max_pct >= limits['warning_threshold'] * 100:
        status = "WARNING"
        color = "orange"
    else:
        status = "OK"
        color = "green"
    
    # Calculate tokens (for AI APIs)
    total_tokens = sum(c.get('tokens', 0) for c in calls)
    
    return {
        "api_name": api_name,
        "display_name": limits['name'],
        "hourly_calls": hourly_calls,
        "hourly_limit": limits['hourly_limit'],
        "hourly_pct": hourly_pct,
        "daily_calls": daily_calls,
        "daily_limit": limits['daily_limit'],
        "daily_pct": daily_pct,
        "total_tokens": total_tokens,
        "status": status,
        "color": color,
        "remaining_hourly": limits['hourly_limit'] - hourly_calls,
        "remaining_daily": limits['daily_limit'] - daily_calls
    }


def get_all_usage_stats():
    """Get usage statistics for all APIs"""
    stats = {}
    for api_name in RATE_LIMITS.keys():
        stats[api_name] = get_usage_stats(api_name)
    return stats


def get_usage_summary():
    """Get summary of all API usage"""
    all_stats = get_all_usage_stats()
    
    total_calls = sum(s['daily_calls'] for s in all_stats.values() if s)
    critical_apis = [s['display_name'] for s in all_stats.values() if s and s['status'] == 'CRITICAL']
    warning_apis = [s['display_name'] for s in all_stats.values() if s and s['status'] == 'WARNING']
    
    return {
        "total_calls_today": total_calls,
        "critical_count": len(critical_apis),
        "warning_count": len(warning_apis),
        "critical_apis": critical_apis,
        "warning_apis": warning_apis,
        "all_ok": len(critical_apis) == 0 and len(warning_apis) == 0
    }


def reset_usage(api_name=None):
    """Reset usage tracking for an API or all APIs"""
    if api_name:
        usage = load_usage()
        if api_name in usage:
            usage[api_name] = {"calls": [], "total": 0}
            save_usage(usage)
    else:
        # Reset all
        save_usage(_init_usage())


def get_estimated_daily_usage():
    """
    Estimate total daily usage based on current usage
    Useful during market hours to project end-of-day usage
    """
    now = datetime.now(IST)
    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    
    # If before market open or after close, return current usage
    if now < market_open or now > market_close:
        all_stats = get_all_usage_stats()
        return {api: stats['daily_calls'] for api, stats in all_stats.items() if stats}
    
    # Calculate elapsed time in market hours
    elapsed_minutes = (now - market_open).total_seconds() / 60
    total_market_minutes = 375  # 6 hours 15 minutes
    
    # Estimate full day usage
    all_stats = get_all_usage_stats()
    estimated = {}
    
    for api, stats in all_stats.items():
        if stats:
            current_calls = stats['daily_calls']
            if elapsed_minutes > 0:
                estimated_total = int((current_calls / elapsed_minutes) * total_market_minutes)
                estimated[api] = {
                    "current": current_calls,
                    "estimated": estimated_total,
                    "limit": stats['daily_limit'],
                    "estimated_pct": (estimated_total / stats['daily_limit']) * 100
                }
            else:
                estimated[api] = {
                    "current": current_calls,
                    "estimated": current_calls,
                    "limit": stats['daily_limit'],
                    "estimated_pct": (current_calls / stats['daily_limit']) * 100
                }
    
    return estimated


def check_rate_limit_alerts():
    """
    Check if any APIs are approaching limits
    Returns list of alerts
    """
    alerts = []
    all_stats = get_all_usage_stats()
    
    for api, stats in all_stats.items():
        if not stats:
            continue
        
        if stats['status'] == 'CRITICAL':
            alerts.append({
                "level": "CRITICAL",
                "api": stats['display_name'],
                "message": f"{stats['display_name']} usage at {stats['daily_pct']:.1f}% of daily limit!",
                "daily_calls": stats['daily_calls'],
                "daily_limit": stats['daily_limit']
            })
        elif stats['status'] == 'WARNING':
            alerts.append({
                "level": "WARNING",
                "api": stats['display_name'],
                "message": f"{stats['display_name']} usage at {stats['daily_pct']:.1f}% of daily limit",
                "daily_calls": stats['daily_calls'],
                "daily_limit": stats['daily_limit']
            })
    
    return alerts
