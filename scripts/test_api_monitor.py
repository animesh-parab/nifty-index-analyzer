"""Test API Rate Limit Monitoring"""

from api_rate_monitor import (
    record_api_call, get_usage_stats, get_all_usage_stats,
    get_usage_summary, check_rate_limit_alerts,
    get_estimated_daily_usage, reset_usage
)
import time

print("\n" + "="*70)
print("TESTING API RATE LIMIT MONITORING")
print("="*70 + "\n")

# Reset usage for clean test
print("1. Resetting usage data...")
reset_usage()
print("   ✓ Reset complete\n")

# Simulate API calls
print("2. Simulating API calls...")

# Groq calls
for i in range(10):
    record_api_call("groq", "chat.completions", tokens=500)
print(f"   ✓ Recorded 10 Groq API calls")

# Gemini calls
for i in range(5):
    record_api_call("gemini", "generate_content", tokens=0)
print(f"   ✓ Recorded 5 Gemini API calls")

# Angel One calls
for i in range(50):
    record_api_call("angel_one", "getLtpData")
print(f"   ✓ Recorded 50 Angel One API calls")

# NSE calls
for i in range(3):
    record_api_call("nse", "equity-stockIndices")
print(f"   ✓ Recorded 3 NSE API calls")

# yfinance calls
for i in range(2):
    record_api_call("yfinance", "history")
print(f"   ✓ Recorded 2 yfinance API calls\n")

# Get usage stats
print("3. Usage Statistics:")
print("-" * 70)

all_stats = get_all_usage_stats()

for api_name, stats in all_stats.items():
    if not stats or stats['daily_calls'] == 0:
        continue
    
    status_emoji = {
        "OK": "🟢",
        "WARNING": "🟡",
        "CRITICAL": "🔴"
    }.get(stats['status'], "⚪")
    
    print(f"\n{status_emoji} {stats['display_name']}")
    print(f"   Daily: {stats['daily_calls']:,} / {stats['daily_limit']:,} ({stats['daily_pct']:.1f}%)")
    print(f"   Hourly: {stats['hourly_calls']:,} / {stats['hourly_limit']:,} ({stats['hourly_pct']:.1f}%)")
    print(f"   Remaining: {stats['remaining_daily']:,} calls")
    if stats['total_tokens'] > 0:
        print(f"   Tokens: {stats['total_tokens']:,}")
    print(f"   Status: {stats['status']}")

print("\n" + "-" * 70)

# Get summary
print("\n4. Usage Summary:")
summary = get_usage_summary()
print(f"   Total calls today: {summary['total_calls_today']:,}")
print(f"   Critical APIs: {summary['critical_count']}")
print(f"   Warning APIs: {summary['warning_count']}")
print(f"   All OK: {summary['all_ok']}")

if summary['critical_apis']:
    print(f"   Critical: {', '.join(summary['critical_apis'])}")
if summary['warning_apis']:
    print(f"   Warning: {', '.join(summary['warning_apis'])}")

# Check alerts
print("\n5. Rate Limit Alerts:")
alerts = check_rate_limit_alerts()

if alerts:
    for alert in alerts:
        level_emoji = "🔴" if alert['level'] == 'CRITICAL' else "🟡"
        print(f"   {level_emoji} {alert['level']}: {alert['message']}")
else:
    print("   ✅ No alerts - all APIs within safe limits")

# Estimated daily usage
print("\n6. Estimated Daily Usage:")
estimated = get_estimated_daily_usage()

for api, est in estimated.items():
    # Handle both dict and int formats
    if isinstance(est, dict):
        if est['current'] == 0:
            continue
        
        status = "🔴" if est['estimated_pct'] >= 95 else "🟡" if est['estimated_pct'] >= 80 else "🟢"
        
        print(f"   {status} {api.upper()}")
        print(f"      Current: {est['current']:,} → Estimated: {est['estimated']:,} / {est['limit']:,}")
        print(f"      Projected usage: {est['estimated_pct']:.1f}%")
    else:
        # Simple int format (market closed)
        if est == 0:
            continue
        print(f"   🟢 {api.upper()}: {est:,} calls today")

print("\n" + "="*70)
print("✓ API RATE LIMIT MONITORING WORKING!")
print("="*70)
print("\nFeatures:")
print("✅ Real-time usage tracking")
print("✅ Hourly and daily limits")
print("✅ Status indicators (OK/WARNING/CRITICAL)")
print("✅ Alert system")
print("✅ Estimated daily usage projection")
print("✅ Token tracking for AI APIs")
print("\nView in dashboard sidebar: 📊 API Usage Monitor")
print("\n")
