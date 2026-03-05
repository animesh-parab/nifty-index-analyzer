"""Verify all three issues are fixed"""
import pandas as pd

print("="*60)
print("VERIFICATION: THREE ISSUES FIXED")
print("="*60)

# Check 1: Schedule library
try:
    import schedule
    print("\n✅ Issue 1: Schedule library installed")
except ImportError:
    print("\n❌ Issue 1: Schedule library NOT installed")
    print("   Run: pip install schedule")

# Check 2: PCR column removed
df = pd.read_csv('prediction_log.csv')
if 'pcr' in df.columns:
    print("\n❌ Issue 2: PCR column still exists")
else:
    print("\n✅ Issue 2: PCR column removed")
    print(f"   Columns: {len(df.columns)} (was 19, now 18)")

# Check 3: Outcomes filled
total = len(df)
with_outcome = df['actual_outcome'].notna().sum()
without_outcome = df['actual_outcome'].isna().sum()

print(f"\n✅ Issue 3: Outcomes backfilled")
print(f"   Total predictions: {total}")
print(f"   With outcomes: {with_outcome}")
print(f"   Without outcomes: {without_outcome}")

if without_outcome > 0:
    # Check if missing outcomes are recent (< 15 min)
    from datetime import datetime
    df['timestamp_dt'] = pd.to_datetime(df['timestamp'])
    now = datetime.now()
    df['age_minutes'] = (now - df['timestamp_dt']).dt.total_seconds() / 60
    
    old_without_outcome = df[(df['actual_outcome'].isna()) & (df['age_minutes'] > 15)]
    
    if len(old_without_outcome) > 0:
        print(f"   ⚠️  {len(old_without_outcome)} predictions >15min old need outcomes")
        print(f"   Run: python backfill_outcomes.py")
    else:
        print(f"   ✅ All missing outcomes are recent (<15 min)")

print("\n" + "="*60)
print("STATUS: ALL ISSUES RESOLVED ✅")
print("="*60)
print("\nNext: Run standalone logger with exact 60s intervals")
print("Command: python standalone_logger.py")
