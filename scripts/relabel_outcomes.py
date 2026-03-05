"""
Relabel outcomes with new threshold: ±0.3% instead of ±0.1%
This will reduce SIDEWAYS samples and increase UP/DOWN samples
"""

import pandas as pd
from datetime import datetime

LOG_FILE = "prediction_log.csv"
BACKUP_FILE = f"backups/prediction_log_before_relabel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

print("="*80)
print("RELABELING OUTCOMES WITH NEW THRESHOLD")
print("="*80)

# Load data
df = pd.read_csv(LOG_FILE)
print(f"\nTotal predictions: {len(df)}")

# Backup
df.to_csv(BACKUP_FILE, index=False)
print(f"Backup saved: {BACKUP_FILE}")

# Count current outcomes
with_outcomes = df['actual_outcome'].notna()
print(f"\nPredictions with outcomes: {with_outcomes.sum()}")

if with_outcomes.sum() == 0:
    print("\n⚠️  No outcomes to relabel!")
    exit(0)

# Show current distribution
print("\nCURRENT DISTRIBUTION (±0.1% threshold):")
current_dist = df[with_outcomes]['actual_outcome'].value_counts().sort_index()
for outcome, count in current_dist.items():
    label = {-1.0: 'DOWN', 0.0: 'SIDEWAYS', 1.0: 'UP'}.get(outcome, outcome)
    pct = (count / with_outcomes.sum()) * 100
    print(f"  {label}: {count} ({pct:.1f}%)")

# Relabel with new threshold (±0.3%)
print("\nRelabeling with NEW THRESHOLD (±0.3%)...")

# We need to recalculate from entry_price
# But we don't have the 15-min price stored
# So we'll use the actual_outcome to infer the price change

# Actually, we need to recalculate properly
# Let's create a function to do this

def relabel_outcome(row):
    """Relabel outcome based on new threshold"""
    if pd.isna(row['actual_outcome']):
        return row['actual_outcome']
    
    # We need the actual price change
    # Since we don't have it stored, we'll need to fetch it again
    # For now, let's use a heuristic based on the current outcome
    
    # This is a limitation - we need the actual 15-min price
    # For proper relabeling, we should re-fetch prices
    return row['actual_outcome']

print("\n⚠️  WARNING: Cannot relabel existing outcomes without 15-min prices")
print("The outcome labeling happens during data collection.")
print("\nTo apply new threshold:")
print("  1. Update prediction_logger.py with new threshold")
print("  2. Collect new data with new threshold")
print("  3. Or manually recalculate outcomes from stored prices")

print("\n" + "="*80)
print("RECOMMENDATION")
print("="*80)
print("\nSince we can't relabel historical data without 15-min prices,")
print("we'll proceed with training using the current data but apply")
print("SMOTE and class weights to handle the imbalance.")
print("\nFor future data collection, update prediction_logger.py")
print("to use ±0.3% threshold instead of ±0.1%")
print("="*80)
