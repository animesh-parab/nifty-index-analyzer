"""
xgb_model.py
XGBoost ML Model for Nifty Prediction

Trains on logged predictions and actual outcomes.
Uses raw indicator values as features (NOT +1/-1 scores).
"""

import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Feature list - raw indicator values (PCR removed - APIs unreliable)
FEATURES = [
    'rsi_14', 'macd_value', 'macd_signal',
    'ema_9', 'ema_21', 'ema_50',
    'bb_position', 'atr_14',
    'vix', 'day_of_week', 'us_market_change'
]

MODEL_PATH = 'xgb_model.pkl'
MIN_SAMPLES = 300  # Minimum samples needed to train


def train_model(log_path='prediction_log.csv') -> dict:
    """
    Train XGBoost model on logged predictions.
    
    Args:
        log_path: Path to prediction log CSV
    
    Returns:
        Dict with training results and metrics
    """
    try:
        # Check if log file exists
        if not os.path.exists(log_path):
            logger.error(f"Log file not found: {log_path}")
            return {
                'success': False,
                'error': 'Log file not found',
                'samples': 0
            }
        
        # Load data
        df = pd.read_csv(log_path)
        
        # Remove rows without outcomes
        df = df.dropna(subset=['actual_outcome'])
        
        samples = len(df)
        logger.info(f"Loaded {samples} samples with outcomes")
        
        # Check minimum samples
        if samples < MIN_SAMPLES:
            logger.warning(f"Not enough data: {samples} samples. Need {MIN_SAMPLES} minimum.")
            return {
                'success': False,
                'error': f'Not enough data: {samples}/{MIN_SAMPLES} samples',
                'samples': samples,
                'required': MIN_SAMPLES
            }
        
        # Prepare features and target
        X = df[FEATURES]
        y = df['actual_outcome']  # 1 (UP), -1 (DOWN), 0 (SIDEWAYS)
        
        # Map outcomes to 0, 1, 2 for XGBoost (expects sequential classes)
        # -1 (DOWN) -> 0, 0 (SIDEWAYS) -> 1, 1 (UP) -> 2
        outcome_map = {-1: 0, 0: 1, 1: 2}
        y_mapped = y.map(outcome_map)
        
        # Check class distribution
        class_counts = y.value_counts()
        logger.info(f"Class distribution:\n{class_counts}")
        
        # Split data (shuffle=False for time series)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_mapped, test_size=0.2, shuffle=False  # CRITICAL: Don't shuffle time series!
        )
        
        logger.info(f"Training set: {len(X_train)} samples")
        logger.info(f"Test set: {len(X_test)} samples")
        
        # Train XGBoost model
        model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric='mlogloss',
            use_label_encoder=False,
            random_state=42
        )
        
        logger.info("Training XGBoost model...")
        model.fit(X_train, y_train)
        
        # Evaluate on test set
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"✓ Model trained successfully!")
        logger.info(f"Test Accuracy: {accuracy:.2%}")
        
        # Detailed metrics
        report = classification_report(y_test, y_pred, output_dict=True)
        conf_matrix = confusion_matrix(y_test, y_pred)
        
        # Feature importance
        feature_importance = dict(zip(FEATURES, model.feature_importances_))
        top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
        
        logger.info("Top 5 features:")
        for feat, importance in top_features:
            logger.info(f"  {feat}: {importance:.4f}")
        
        # Save model
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model, f)
        
        logger.info(f"✓ Model saved to {MODEL_PATH}")
        
        return {
            'success': True,
            'accuracy': round(accuracy * 100, 2),
            'samples': samples,
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'class_distribution': class_counts.to_dict(),
            'classification_report': report,
            'confusion_matrix': conf_matrix.tolist(),
            'top_features': top_features,
            'model_path': MODEL_PATH,
            'trained_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error training model: {e}")
        return {
            'success': False,
            'error': str(e),
            'samples': 0
        }


def load_model():
    """Load trained XGBoost model from disk."""
    try:
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as f:
                model = pickle.load(f)
            logger.info(f"✓ Model loaded from {MODEL_PATH}")
            return model
        else:
            logger.warning(f"Model file not found: {MODEL_PATH}")
            return None
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None


def predict(indicator_values: dict) -> tuple:
    """
    Make prediction using trained XGBoost model.
    
    Args:
        indicator_values: Dict of feature name → raw value
    
    Returns:
        Tuple of (direction, confidence)
        - direction: 1 (UP), -1 (DOWN), 0 (SIDEWAYS)
        - confidence: 0-100 (probability * 100)
        
        Returns (None, None) if model not available
    """
    try:
        # Load model
        model = load_model()
        
        if model is None:
            return None, None  # Fall back to rule-based
        
        # Prepare features
        X = pd.DataFrame([indicator_values])[FEATURES]
        
        # Get prediction and probabilities
        direction_mapped = model.predict(X)[0]
        proba = model.predict_proba(X)[0]
        
        # Map back: 0 -> -1 (DOWN), 1 -> 0 (SIDEWAYS), 2 -> 1 (UP)
        reverse_map = {0: -1, 1: 0, 2: 1}
        direction = reverse_map[int(direction_mapped)]
        
        # Confidence is the max probability
        confidence = round(max(proba) * 100, 1)
        
        logger.info(f"XGBoost prediction: {direction} (confidence: {confidence}%)")
        
        return int(direction), confidence
        
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        return None, None


def get_model_info() -> dict:
    """Get information about the trained model."""
    try:
        if not os.path.exists(MODEL_PATH):
            return {
                'exists': False,
                'message': 'Model not trained yet'
            }
        
        # Get file info
        file_stats = os.stat(MODEL_PATH)
        file_size = file_stats.st_size / 1024  # KB
        modified_time = datetime.fromtimestamp(file_stats.st_mtime)
        
        # Load model to get details
        model = load_model()
        
        if model is None:
            return {
                'exists': True,
                'error': 'Failed to load model'
            }
        
        return {
            'exists': True,
            'file_size_kb': round(file_size, 2),
            'last_modified': modified_time.isoformat(),
            'n_estimators': model.n_estimators,
            'max_depth': model.max_depth,
            'learning_rate': model.learning_rate,
            'features': FEATURES,
            'n_features': len(FEATURES)
        }
        
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        return {
            'exists': False,
            'error': str(e)
        }


if __name__ == "__main__":
    # Test training
    print("XGBoost Model Training Test")
    print("=" * 50)
    
    result = train_model()
    
    if result['success']:
        print(f"✓ Training successful!")
        print(f"  Accuracy: {result['accuracy']}%")
        print(f"  Samples: {result['samples']}")
        print(f"  Train/Test: {result['train_samples']}/{result['test_samples']}")
        print(f"\nClass distribution:")
        for cls, count in result['class_distribution'].items():
            print(f"  {cls}: {count}")
        print(f"\nTop features:")
        for feat, importance in result['top_features']:
            print(f"  {feat}: {importance:.4f}")
    else:
        print(f"✗ Training failed: {result['error']}")
        print(f"  Samples: {result['samples']}/{result.get('required', MIN_SAMPLES)}")
