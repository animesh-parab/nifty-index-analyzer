"""
weekly_retrain.py

Automated weekly XGBoost retraining script
Runs every Sunday at 8 PM to retrain on latest prediction_log.csv

Features:
- Automatic training on latest data
- Comparison with previous week
- Saves model if accuracy improved
- Generates detailed report
- Logs all results

Usage: python weekly_retrain.py
Scheduled: Windows Task Scheduler (every Sunday 8 PM)
"""

import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
import pickle
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration
MIN_SAMPLES = 300  # Minimum samples needed for training
REPORT_DIR = 'logs/retraining'
MODEL_DIR = 'models/weekly'
CURRENT_MODEL = 'xgb_model_baseline.pkl'

# Create directories if they don't exist
os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# Get current date
now = datetime.now()
date_str = now.strftime('%Y-%m-%d')
time_str = now.strftime('%Y-%m-%d %H:%M:%S')

# Start report
report_lines = []
report_lines.append("="*70)
report_lines.append("WEEKLY XGBOOST RETRAINING REPORT")
report_lines.append("="*70)
report_lines.append(f"Date: {time_str}")
report_lines.append("="*70)
report_lines.append("")

print("="*70)
print("WEEKLY XGBOOST RETRAINING")
print("="*70)
print(f"Date: {time_str}")
print("="*70)
print()

# Step 1: Load data
print("Step 1: Loading prediction_log.csv...")
report_lines.append("Step 1: Loading prediction_log.csv")

try:
    df = pd.read_csv('prediction_log.csv', on_bad_lines='skip')
    print(f"✅ Loaded {len(df)} rows")
    report_lines.append(f"✅ Loaded {len(df)} rows")
except Exception as e:
    print(f"❌ Error loading file: {e}")
    report_lines.append(f"❌ Error loading file: {e}")
    report_lines.append("")
    report_lines.append("TRAINING ABORTED - Cannot load data")
    
    # Save report
    report_path = os.path.join(REPORT_DIR, f'{date_str}_report.txt')
    with open(report_path, 'w') as f:
        f.write('\n'.join(report_lines))
    
    exit(1)

# Remove rows without outcomes
df = df.dropna(subset=['actual_outcome'])
print(f"✅ Rows with outcomes: {len(df)}")
report_lines.append(f"✅ Rows with outcomes: {len(df)}")

# Check minimum samples
if len(df) < MIN_SAMPLES:
    print(f"⚠️  Warning: Only {len(df)} samples (need {MIN_SAMPLES}+)")
    print("   Training may not be reliable with this few samples.")
    report_lines.append(f"⚠️  Warning: Only {len(df)} samples (need {MIN_SAMPLES}+)")
    report_lines.append("   Training may not be reliable with this few samples.")

report_lines.append("")

# Features
FEATURES = [
    'rsi_14', 'macd_value', 'macd_signal', 'ema_9', 'ema_21', 'ema_50',
    'bb_position', 'atr_14', 'vix', 'day_of_week', 'us_market_change'
]

# Step 2: Prepare data
print("Step 2: Preparing features and labels...")
report_lines.append("Step 2: Preparing features and labels")

X = df[FEATURES].copy()
y = df['actual_outcome'].map({-1: 0, 0: 1, 1: 2})

# Fill missing values
missing = X.isnull().sum().sum()
if missing > 0:
    print(f"⚠️  Filled {missing} missing values with 0")
    report_lines.append(f"⚠️  Filled {missing} missing values with 0")
    X = X.fillna(0)

print(f"✅ Features: {len(FEATURES)} columns")
report_lines.append(f"✅ Features: {len(FEATURES)} columns")
report_lines.append("")

# Step 3: Class distribution
print("Step 3: Class distribution:")
report_lines.append("Step 3: Class distribution")
report_lines.append("-" * 50)

class_counts = y.value_counts().sort_index()
total = len(y)
for cls, count in class_counts.items():
    label = {0: 'DOWN', 1: 'SIDEWAYS', 2: 'UP'}.get(cls, 'UNKNOWN')
    percentage = (count / total) * 100
    line = f"   {label:10s}: {count:5d} ({percentage:5.1f}%)"
    print(line)
    report_lines.append(line)

line = f"   {'TOTAL':10s}: {total:5d} (100.0%)"
print(line)
report_lines.append(line)
report_lines.append("-" * 50)
report_lines.append("")

# Step 4: Split data
print("Step 4: Splitting data (80% train, 20% test)...")
report_lines.append("Step 4: Splitting data (80% train, 20% test)")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=False, random_state=42
)

print(f"✅ Training set: {len(X_train)} samples")
print(f"✅ Test set: {len(X_test)} samples")
report_lines.append(f"✅ Training set: {len(X_train)} samples")
report_lines.append(f"✅ Test set: {len(X_test)} samples")
report_lines.append("")

# Step 5: Apply SMOTE
print("Step 5: Applying SMOTE...")
report_lines.append("Step 5: Applying SMOTE")

smote = SMOTE(random_state=42)
X_balanced, y_balanced = smote.fit_resample(X_train, y_train)

print(f"✅ Balanced training set: {len(X_balanced)} samples")
report_lines.append(f"✅ Balanced training set: {len(X_balanced)} samples")

# Show balanced distribution
balanced_counts = pd.Series(y_balanced).value_counts().sort_index()
for cls, count in balanced_counts.items():
    label = {0: 'DOWN', 1: 'SIDEWAYS', 2: 'UP'}.get(cls, 'UNKNOWN')
    percentage = (count / len(y_balanced)) * 100
    report_lines.append(f"   {label:10s}: {count:5d} ({percentage:5.1f}%)")

report_lines.append("")

# Step 6: Calculate weights
print("Step 6: Calculating sample weights...")
report_lines.append("Step 6: Calculating sample weights")

counter = Counter(y_balanced)
total_balanced = len(y_balanced)
weights = {cls: total_balanced/count for cls, count in counter.items()}
sample_weights = np.array([weights[label] for label in y_balanced])

for cls, weight in weights.items():
    label = {0: 'DOWN', 1: 'SIDEWAYS', 2: 'UP'}.get(cls, 'UNKNOWN')
    report_lines.append(f"   {label:10s}: {weight:.4f}")

report_lines.append("")

# Step 7: Train model
print("Step 7: Training XGBoost model...")
report_lines.append("Step 7: Training XGBoost model")
report_lines.append("   Settings: n_estimators=300, max_depth=6, lr=0.03")

model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.03,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric='mlogloss',
    use_label_encoder=False,
    random_state=42
)

model.fit(X_balanced, y_balanced, sample_weight=sample_weights, verbose=False)

print("✅ Model training complete!")
report_lines.append("✅ Model training complete!")
report_lines.append("")

# Step 8: Evaluate
print("Step 8: Evaluating model...")
report_lines.append("Step 8: Evaluating model")

y_pred = model.predict(X_test)

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)

report_lines.append("")
report_lines.append("CONFUSION MATRIX:")
report_lines.append("-" * 50)
report_lines.append(f"{'':15s} {'PREDICTED':^40s}")
report_lines.append(f"{'':15s} {'DOWN':>12s} {'SIDEWAYS':>12s} {'UP':>12s}")
report_lines.append("-" * 50)

labels = ['DOWN', 'SIDEWAYS', 'UP']
for i, label in enumerate(labels):
    if i == 0:
        line = f"{'ACTUAL':15s}{label:>12s}"
    else:
        line = f"{'':15s}{label:>12s}"
    
    for j in range(3):
        line += f"{cm[i][j]:>12d}"
    
    report_lines.append(line)

report_lines.append("-" * 50)
report_lines.append("")

# Per-class accuracy
report_lines.append("PER-CLASS ACCURACY:")
report_lines.append("-" * 50)

per_class_acc = []
for i, label in enumerate(labels):
    class_total = cm[i].sum()
    class_correct = cm[i][i]
    class_accuracy = (class_correct / class_total * 100) if class_total > 0 else 0
    per_class_acc.append(class_accuracy)
    line = f"   {label:10s}: {class_correct:4d}/{class_total:4d} correct ({class_accuracy:5.1f}%)"
    print(line)
    report_lines.append(line)

report_lines.append("-" * 50)
report_lines.append("")

# Overall accuracy
overall_accuracy = accuracy_score(y_test, y_pred) * 100
balanced_accuracy = np.mean(per_class_acc)

report_lines.append("OVERALL METRICS:")
report_lines.append("-" * 50)
report_lines.append(f"   Test Accuracy: {overall_accuracy:.2f}%")
report_lines.append(f"   Balanced Accuracy: {balanced_accuracy:.2f}%")
report_lines.append("-" * 50)
report_lines.append("")

print(f"✅ Test Accuracy: {overall_accuracy:.2f}%")
print(f"✅ Balanced Accuracy: {balanced_accuracy:.2f}%")

# Feature importance
feature_importance = model.feature_importances_
importance_df = pd.DataFrame({
    'feature': FEATURES,
    'importance': feature_importance
}).sort_values('importance', ascending=False)

report_lines.append("FEATURE IMPORTANCE (Top 5):")
report_lines.append("-" * 50)
for idx, row in importance_df.head(5).iterrows():
    report_lines.append(f"   {row['feature']:20s}: {row['importance']:.4f}")
report_lines.append("-" * 50)
report_lines.append("")

# Step 9: Compare with previous model
print()
print("Step 9: Comparing with previous model...")
report_lines.append("Step 9: Comparing with previous model")

previous_accuracy = None
if os.path.exists(CURRENT_MODEL):
    try:
        with open(CURRENT_MODEL, 'rb') as f:
            old_model = pickle.load(f)
        
        y_pred_old = old_model.predict(X_test)
        previous_accuracy = accuracy_score(y_test, y_pred_old) * 100
        
        improvement = overall_accuracy - previous_accuracy
        
        print(f"   Previous accuracy: {previous_accuracy:.2f}%")
        print(f"   Current accuracy: {overall_accuracy:.2f}%")
        print(f"   Improvement: {improvement:+.2f}%")
        
        report_lines.append(f"   Previous accuracy: {previous_accuracy:.2f}%")
        report_lines.append(f"   Current accuracy: {overall_accuracy:.2f}%")
        report_lines.append(f"   Improvement: {improvement:+.2f}%")
        
        if improvement > 0:
            print("   ✅ Model improved!")
            report_lines.append("   ✅ Model improved!")
        elif improvement < -5:
            print("   ⚠️  Warning: Accuracy dropped significantly!")
            report_lines.append("   ⚠️  Warning: Accuracy dropped significantly!")
        else:
            print("   ℹ️  Similar performance")
            report_lines.append("   ℹ️  Similar performance")
            
    except Exception as e:
        print(f"   ⚠️  Could not load previous model: {e}")
        report_lines.append(f"   ⚠️  Could not load previous model: {e}")
else:
    print("   ℹ️  No previous model found")
    report_lines.append("   ℹ️  No previous model found")

report_lines.append("")

# Step 10: Save model
print()
print("Step 10: Saving model...")
report_lines.append("Step 10: Saving model")

# Save weekly model
weekly_model_path = os.path.join(MODEL_DIR, f'xgb_model_{date_str}.pkl')
try:
    with open(weekly_model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"✅ Saved weekly model: {weekly_model_path}")
    report_lines.append(f"✅ Saved weekly model: {weekly_model_path}")
except Exception as e:
    print(f"❌ Error saving weekly model: {e}")
    report_lines.append(f"❌ Error saving weekly model: {e}")

# Update baseline model if improved
if previous_accuracy is None or overall_accuracy > previous_accuracy:
    try:
        with open(CURRENT_MODEL, 'wb') as f:
            pickle.dump(model, f)
        print(f"✅ Updated baseline model: {CURRENT_MODEL}")
        report_lines.append(f"✅ Updated baseline model: {CURRENT_MODEL}")
    except Exception as e:
        print(f"❌ Error updating baseline model: {e}")
        report_lines.append(f"❌ Error updating baseline model: {e}")
else:
    print(f"ℹ️  Baseline model not updated (no improvement)")
    report_lines.append(f"ℹ️  Baseline model not updated (no improvement)")

report_lines.append("")

# Step 11: Recommendations
print()
print("Step 11: Generating recommendations...")
report_lines.append("Step 11: Recommendations")
report_lines.append("-" * 50)

if len(df) < 700:
    report_lines.append("   📊 Continue daily data collection")
    report_lines.append(f"   Current: {len(df)} samples, Target: 1000+")
    report_lines.append("   Expected: 2-3 more weeks of collection")
elif len(df) < 1000:
    report_lines.append("   📊 Good progress on data collection")
    report_lines.append(f"   Current: {len(df)} samples, Target: 1000+")
    report_lines.append("   Expected: 1-2 more weeks of collection")
else:
    report_lines.append("   ✅ Target sample count reached!")
    report_lines.append(f"   Current: {len(df)} samples")

if overall_accuracy < 45:
    report_lines.append("   ⚙️  Keep current weights: XGBoost 30%, AI 35% each")
    report_lines.append("   Model accuracy still below 45%")
elif overall_accuracy < 55:
    report_lines.append("   ⚙️  Consider increasing XGBoost weight to 40%")
    report_lines.append("   Model accuracy 45-55%, showing improvement")
elif overall_accuracy < 60:
    report_lines.append("   ⚙️  Increase XGBoost weight to 50%")
    report_lines.append("   Model accuracy 55-60%, good performance")
else:
    report_lines.append("   ✅ Increase XGBoost weight to 60%")
    report_lines.append("   Model accuracy >60%, excellent performance!")

report_lines.append("-" * 50)
report_lines.append("")

# Summary
report_lines.append("="*70)
report_lines.append("SUMMARY")
report_lines.append("="*70)
report_lines.append(f"Date: {date_str}")
report_lines.append(f"Samples: {len(df)}")
report_lines.append(f"Training samples: {len(X_train)} → {len(X_balanced)} (after SMOTE)")
report_lines.append(f"Test samples: {len(X_test)}")
report_lines.append(f"Overall accuracy: {overall_accuracy:.2f}%")
report_lines.append(f"Balanced accuracy: {balanced_accuracy:.2f}%")

if previous_accuracy is not None:
    improvement = overall_accuracy - previous_accuracy
    report_lines.append(f"Improvement: {improvement:+.2f}%")

report_lines.append("")
report_lines.append("Next retraining: Next Sunday at 8 PM")
report_lines.append("="*70)

# Save report
report_path = os.path.join(REPORT_DIR, f'{date_str}_report.txt')
with open(report_path, 'w') as f:
    f.write('\n'.join(report_lines))

print()
print("="*70)
print("WEEKLY RETRAINING COMPLETE")
print("="*70)
print(f"Report saved: {report_path}")
print(f"Model saved: {weekly_model_path}")
print()
print(f"Overall accuracy: {overall_accuracy:.2f}%")
print(f"Balanced accuracy: {balanced_accuracy:.2f}%")
print()
print("Next retraining: Next Sunday at 8 PM")
print("="*70)
