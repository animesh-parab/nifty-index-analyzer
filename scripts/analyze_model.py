"""
Analyze trained XGBoost model performance
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

# Load data
df = pd.read_csv('prediction_log.csv', on_bad_lines='skip')
df = df.dropna(subset=['actual_outcome'])

X = df[FEATURES]
y = df['actual_outcome']

# Map outcomes
outcome_map = {-1: 0, 0: 1, 1: 2}
y_mapped = y.map(outcome_map)

# Split (same as training)
X_train, X_test, y_train, y_test = train_test_split(
    X, y_mapped, test_size=0.2, shuffle=False
)

# Load model
with open('xgb_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Predict
y_pred = model.predict(X_test)

print("="*70)
print("MODEL PERFORMANCE ANALYSIS")
print("="*70)

print("\nConfusion Matrix:")
print("                Predicted")
print("              DOWN  SIDEWAYS  UP")
cm = confusion_matrix(y_test, y_pred)
labels = ['DOWN', 'SIDEWAYS', 'UP']
for i, label in enumerate(labels):
    print(f"Actual {label:8s}  {cm[i][0]:4d}  {cm[i][1]:8d}  {cm[i][2]:2d}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['DOWN', 'SIDEWAYS', 'UP'], zero_division=0))

print("\nTest Set Distribution:")
test_dist = pd.Series(y_test).value_counts().sort_index()
for cls, count in test_dist.items():
    label = {0: 'DOWN', 1: 'SIDEWAYS', 2: 'UP'}[cls]
    print(f"  {label}: {count}")

print("\nPrediction Distribution:")
pred_dist = pd.Series(y_pred).value_counts().sort_index()
for cls, count in pred_dist.items():
    label = {0: 'DOWN', 1: 'SIDEWAYS', 2: 'UP'}[cls]
    print(f"  {label}: {count}")

print("="*70)
