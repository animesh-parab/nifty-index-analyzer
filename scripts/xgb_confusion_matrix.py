"""
Generate detailed confusion matrix and analysis for XGBoost model
"""

import pickle
import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split

FEATURES = [
    'rsi_14', 'macd_value', 'macd_signal',
    'ema_9', 'ema_21', 'ema_50',
    'bb_position', 'atr_14',
    'vix', 'day_of_week', 'us_market_change'
]

print("="*80)
print("XGBOOST MODEL - CONFUSION MATRIX & DETAILED ANALYSIS")
print("="*80)

# Load data
df = pd.read_csv('prediction_log.csv', on_bad_lines='skip')
df = df.dropna(subset=['actual_outcome'])

print(f"\nTotal samples: {len(df)}")

X = df[FEATURES]
y = df['actual_outcome']

# Map outcomes: -1 (DOWN) -> 0, 0 (SIDEWAYS) -> 1, 1 (UP) -> 2
outcome_map = {-1: 0, 0: 1, 1: 2}
y_mapped = y.map(outcome_map)

# Split (same as training)
X_train, X_test, y_train, y_test = train_test_split(
    X, y_mapped, test_size=0.2, shuffle=False
)

print(f"Training samples: {len(X_train)}")
print(f"Test samples: {len(X_test)}")

# Load model
with open('xgb_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Predict
y_pred = model.predict(X_test)

# Get actual class names
class_names = ['DOWN (-1)', 'SIDEWAYS (0)', 'UP (+1)']

print("\n" + "="*80)
print("CONFUSION MATRIX")
print("="*80)

cm = confusion_matrix(y_test, y_pred)

print("\n                    PREDICTED")
print("                DOWN    SIDEWAYS    UP")
print("              ------  ----------  ------")

for i, actual_label in enumerate(class_names):
    print(f"ACTUAL {actual_label:12s}  {cm[i][0]:4d}    {cm[i][1]:6d}    {cm[i][2]:4d}")

print("\n" + "="*80)
print("INTERPRETATION")
print("="*80)

# Calculate metrics for each class
for i, label in enumerate(class_names):
    actual_count = cm[i].sum()
    correct = cm[i][i]
    accuracy = (correct / actual_count * 100) if actual_count > 0 else 0
    
    print(f"\n{label}:")
    print(f"  Total in test set: {actual_count}")
    print(f"  Correctly predicted: {correct}")
    print(f"  Accuracy: {accuracy:.1f}%")
    
    # Show misclassifications
    misclassified = []
    for j in range(3):
        if i != j and cm[i][j] > 0:
            misclassified.append(f"{cm[i][j]} as {class_names[j]}")
    
    if misclassified:
        print(f"  Misclassified: {', '.join(misclassified)}")

print("\n" + "="*80)
print("PREDICTION DISTRIBUTION")
print("="*80)

print("\nACTUAL (Test Set):")
actual_dist = pd.Series(y_test).value_counts().sort_index()
for cls, count in actual_dist.items():
    pct = (count / len(y_test)) * 100
    print(f"  {class_names[cls]}: {count} ({pct:.1f}%)")

print("\nPREDICTED (By Model):")
pred_dist = pd.Series(y_pred).value_counts().sort_index()
for cls, count in pred_dist.items():
    pct = (count / len(y_pred)) * 100
    print(f"  {class_names[cls]}: {count} ({pct:.1f}%)")

print("\n" + "="*80)
print("DETAILED CLASSIFICATION REPORT")
print("="*80)

report = classification_report(y_test, y_pred, target_names=class_names, zero_division=0)
print("\n" + report)

print("\n" + "="*80)
print("KEY INSIGHTS")
print("="*80)

# Overall accuracy
overall_accuracy = (cm.diagonal().sum() / cm.sum()) * 100
print(f"\nOverall Accuracy: {overall_accuracy:.2f}%")

# Which class is predicted most?
most_predicted_class = pred_dist.idxmax()
most_predicted_count = pred_dist.max()
print(f"\nMost Predicted Class: {class_names[most_predicted_class]}")
print(f"  Predicted {most_predicted_count} times ({most_predicted_count/len(y_pred)*100:.1f}%)")

# Which class is most accurate?
class_accuracies = []
for i in range(3):
    if cm[i].sum() > 0:
        acc = cm[i][i] / cm[i].sum() * 100
        class_accuracies.append((class_names[i], acc))

class_accuracies.sort(key=lambda x: x[1], reverse=True)
print(f"\nMost Accurate Class: {class_accuracies[0][0]} ({class_accuracies[0][1]:.1f}%)")
print(f"Least Accurate Class: {class_accuracies[-1][0]} ({class_accuracies[-1][1]:.1f}%)")

# Bias analysis
print("\n" + "="*80)
print("BIAS ANALYSIS")
print("="*80)

print("\nIs the model biased toward any class?")
for i, label in enumerate(class_names):
    actual_pct = (actual_dist.get(i, 0) / len(y_test)) * 100
    pred_pct = (pred_dist.get(i, 0) / len(y_pred)) * 100
    bias = pred_pct - actual_pct
    
    if abs(bias) > 10:
        print(f"  {label}: {'OVER' if bias > 0 else 'UNDER'}-predicted by {abs(bias):.1f}%")
    else:
        print(f"  {label}: Balanced (bias: {bias:+.1f}%)")

print("\n" + "="*80)
print("RECOMMENDATIONS")
print("="*80)

if overall_accuracy < 50:
    print("\n⚠️  Model accuracy is below 50% - needs improvement")
    print("\nSuggestions:")
    print("  1. Collect more training data (target: 1000+ samples)")
    print("  2. Add more features (volume, order flow, etc.)")
    print("  3. Try different model parameters")
    print("  4. Consider feature engineering")
    print("  5. Check for data quality issues")
else:
    print("\n✅ Model accuracy is acceptable for market prediction")
    print("\nNext steps:")
    print("  1. Continue collecting data")
    print("  2. Retrain weekly with new data")
    print("  3. Monitor live performance")
    print("  4. Use in ensemble with AI models")

print("\n" + "="*80)
