# Requirements Document: XGBoost Model Improvement

## Introduction

This feature enhances the NIFTY AI Predictor's XGBoost model to achieve 60%+ prediction accuracy through systematic class balancing, advanced analysis capabilities, and trading support features. The current model suffers from class imbalance (48.8% SIDEWAYS bias) resulting in 40.66% accuracy with 95% SIDEWAYS predictions. This improvement addresses the core prediction engine while adding confusion matrix analysis, scenario analysis, and trading level support.

## Glossary

- **XGBoost_Model**: Machine learning classifier predicting market direction (DOWN/SIDEWAYS/UP) using technical indicators
- **SMOTE**: Synthetic Minority Over-sampling Technique for balancing training data classes
- **Class_Weights**: Numerical weights applied during training to balance class importance
- **Confusion_Matrix**: Table showing actual vs predicted outcomes for model evaluation
- **Sideways_Threshold**: Price change percentage defining SIDEWAYS classification (currently ±0.1%, target ±0.3%)
- **Training_Pipeline**: Complete process from data loading through model training to evaluation
- **Prediction_Engine**: System combining XGBoost, Groq AI, and Gemini AI for consensus predictions
- **Support_Resistance_Analyzer**: Component identifying key price levels for trading decisions
- **Scenario_Analyzer**: Component evaluating market conditions and generating trading strategies
- **News_Sentiment_Engine**: Component analyzing news impact on market predictions

## Requirements

### Requirement 1: Enhanced Class Balancing

**User Story:** As a data scientist, I want the XGBoost model to apply multiple class balancing techniques together, so that predictions are not biased toward SIDEWAYS outcomes.

#### Acceptance Criteria

1. WHEN training data is loaded, THE Training_Pipeline SHALL apply a sideways threshold of ±0.3% to classify outcomes
2. WHEN the sideways threshold is applied, THE Training_Pipeline SHALL relabel all historical outcomes using the new threshold
3. WHEN training data has class imbalance, THE Training_Pipeline SHALL apply SMOTE oversampling to balance all three classes to equal counts
4. WHEN SMOTE is applied, THE Training_Pipeline SHALL generate synthetic samples for minority classes (DOWN and UP)
5. WHEN the model is trained, THE Training_Pipeline SHALL calculate and apply class weights inversely proportional to class frequencies
6. WHEN class weights are calculated, THE Training_Pipeline SHALL use the formula: weight = total_samples / (num_classes * class_count)
7. FOR ALL training runs, applying SMOTE then training with class weights SHALL produce equivalent results to training with class weights then applying SMOTE (order independence property)
8. THE Training_Pipeline SHALL log the before and after class distributions showing balanced training data

### Requirement 2: Confusion Matrix Analysis

**User Story:** As a model evaluator, I want to generate and visualize confusion matrices, so that I can understand which predictions are correct and where the model fails.

#### Acceptance Criteria

1. WHEN model evaluation is performed, THE Confusion_Matrix SHALL display actual outcomes on rows and predicted outcomes on columns
2. WHEN the confusion matrix is generated, THE Confusion_Matrix SHALL calculate per-class accuracy as (correct_predictions / total_actual) for each class
3. WHEN the confusion matrix is displayed, THE Confusion_Matrix SHALL show counts for all nine combinations (DOWN/SIDEWAYS/UP × DOWN/SIDEWAYS/UP)
4. WHEN per-class metrics are calculated, THE Confusion_Matrix SHALL compute precision, recall, and F1-score for each class
5. WHEN the model predicts all samples, THE Confusion_Matrix SHALL calculate balanced accuracy as the average of per-class accuracies
6. THE Confusion_Matrix SHALL generate a visual heatmap showing prediction patterns
7. THE Confusion_Matrix SHALL identify the most common misclassification patterns
8. FOR ALL confusion matrices, the sum of all cells SHALL equal the total number of test samples (completeness property)

### Requirement 3: Model Training Pipeline

**User Story:** As a developer, I want an automated training pipeline, so that I can retrain the model with consistent settings and reproducible results.

#### Acceptance Criteria

1. WHEN the training pipeline starts, THE Training_Pipeline SHALL load data from prediction_log.csv and validate all required features are present
2. WHEN data is loaded, THE Training_Pipeline SHALL remove rows with missing actual_outcome values
3. WHEN data is validated, THE Training_Pipeline SHALL verify minimum sample count of 300 before training
4. WHEN data is split, THE Training_Pipeline SHALL use 80% for training and 20% for testing with shuffle=False to preserve time-series order
5. WHEN the model is configured, THE XGBoost_Model SHALL use n_estimators=200, max_depth=4, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8
6. WHEN training completes, THE Training_Pipeline SHALL save the model to xgb_model_balanced.pkl
7. WHEN training completes, THE Training_Pipeline SHALL generate a training report with accuracy, balanced accuracy, confusion matrix, and feature importance
8. THE Training_Pipeline SHALL log all hyperparameters and random seeds for reproducibility
9. FOR ALL valid training datasets, training twice with the same random seed SHALL produce identical models (determinism property)

### Requirement 4: Model Evaluation Metrics

**User Story:** As a model evaluator, I want comprehensive evaluation metrics, so that I can assess model performance beyond simple accuracy.

#### Acceptance Criteria

1. WHEN model evaluation runs, THE Training_Pipeline SHALL calculate overall accuracy as (correct_predictions / total_predictions)
2. WHEN balanced accuracy is calculated, THE Training_Pipeline SHALL compute the average of per-class recall values
3. WHEN per-class metrics are computed, THE Training_Pipeline SHALL calculate precision as (true_positives / predicted_positives) for each class
4. WHEN per-class metrics are computed, THE Training_Pipeline SHALL calculate recall as (true_positives / actual_positives) for each class
5. WHEN F1-scores are calculated, THE Training_Pipeline SHALL use the formula: 2 * (precision * recall) / (precision + recall)
6. WHEN feature importance is analyzed, THE Training_Pipeline SHALL rank all 11 features by their XGBoost importance scores
7. THE Training_Pipeline SHALL display the top 5 most important features with their importance values
8. THE Training_Pipeline SHALL compare current model performance against baseline (40.66% accuracy)

### Requirement 5: Scenario Analysis Engine

**User Story:** As a trader, I want scenario analysis capabilities, so that I can understand how the model would predict under different market conditions.

#### Acceptance Criteria

1. WHEN scenario analysis is requested, THE Scenario_Analyzer SHALL accept market data including price, indicators, news sentiment, and global cues
2. WHEN XGBoost prediction is generated, THE Scenario_Analyzer SHALL extract the prediction direction, confidence, and probability distribution
3. WHEN AI predictions are generated, THE Scenario_Analyzer SHALL query both Groq and Gemini APIs with the same market context
4. WHEN all predictions are collected, THE Scenario_Analyzer SHALL calculate weighted consensus using configurable weights (default: XGBoost 60%, Groq 20%, Gemini 20%)
5. WHEN full agreement exists, THE Scenario_Analyzer SHALL boost final confidence by 10 percentage points
6. WHEN predictions disagree, THE Scenario_Analyzer SHALL flag the disagreement and reduce confidence
7. THE Scenario_Analyzer SHALL generate opening, mid-day, and closing predictions with separate confidence levels
8. THE Scenario_Analyzer SHALL identify key risk factors and catalysts affecting the prediction
9. THE Scenario_Analyzer SHALL output predictions in structured format with direction, confidence, reasoning, and timeframes

### Requirement 6: Support and Resistance Analysis

**User Story:** As a trader, I want automated support and resistance level identification, so that I can make informed entry and exit decisions.

#### Acceptance Criteria

1. WHEN support/resistance analysis is requested, THE Support_Resistance_Analyzer SHALL accept current price and historical price data
2. WHEN resistance levels are calculated, THE Support_Resistance_Analyzer SHALL identify at least 4 resistance levels above current price
3. WHEN support levels are calculated, THE Support_Resistance_Analyzer SHALL identify at least 4 support levels below current price
4. WHEN levels are identified, THE Support_Resistance_Analyzer SHALL classify each level as immediate, strong, major, or critical based on historical price reactions
5. WHEN price approaches a level, THE Support_Resistance_Analyzer SHALL calculate the distance in points and percentage
6. THE Support_Resistance_Analyzer SHALL identify psychological levels (round numbers like 24,000, 25,000)
7. THE Support_Resistance_Analyzer SHALL identify previous day's high, low, and close as key levels
8. THE Support_Resistance_Analyzer SHALL rank levels by strength based on number of touches and volume at those levels

### Requirement 7: Trading Strategy Generator

**User Story:** As a trader, I want automated trading strategy recommendations, so that I can execute trades based on model predictions.

#### Acceptance Criteria

1. WHEN a bearish prediction is made, THE Scenario_Analyzer SHALL generate PE (put option) buying strategies with entry points, stop losses, and targets
2. WHEN a bullish prediction is made, THE Scenario_Analyzer SHALL generate CE (call option) buying strategies with entry points, stop losses, and targets
3. WHEN entry points are generated, THE Scenario_Analyzer SHALL provide at least 3 entry scenarios (aggressive, moderate, conservative)
4. WHEN stop losses are calculated, THE Scenario_Analyzer SHALL provide tight, moderate, and wide stop loss levels
5. WHEN profit targets are set, THE Scenario_Analyzer SHALL provide 3 target levels with probability estimates
6. WHEN strike selection is recommended, THE Scenario_Analyzer SHALL suggest ATM, OTM, and ITM options with risk-reward ratios
7. THE Scenario_Analyzer SHALL calculate position sizing recommendations based on risk percentage (2-3% of capital)
8. THE Scenario_Analyzer SHALL identify optimal trading times (opening volatility, post-bounce, breakdown confirmation)
9. THE Scenario_Analyzer SHALL generate risk management rules including time-based exits and theta decay warnings

### Requirement 8: News Sentiment Integration

**User Story:** As a trader, I want news sentiment analysis integrated into predictions, so that the model considers fundamental factors beyond technical indicators.

#### Acceptance Criteria

1. WHEN news analysis is performed, THE News_Sentiment_Engine SHALL fetch recent news headlines from configured RSS feeds
2. WHEN headlines are collected, THE News_Sentiment_Engine SHALL send them to Groq and Gemini APIs for sentiment scoring
3. WHEN sentiment is scored, THE News_Sentiment_Engine SHALL return a value between -1.0 (extremely bearish) and +1.0 (extremely bullish)
4. WHEN major events are detected, THE News_Sentiment_Engine SHALL flag them as high-impact catalysts (war, policy changes, economic data)
5. WHEN news contradicts technical indicators, THE Scenario_Analyzer SHALL document the conflict and adjust confidence accordingly
6. THE News_Sentiment_Engine SHALL categorize news by type (geopolitical, economic, corporate, technical)
7. THE News_Sentiment_Engine SHALL extract key themes and their impact on market direction
8. FOR ALL news items, the sentiment score SHALL be consistent when analyzed multiple times with the same content (consistency property)

### Requirement 9: Model Comparison and Versioning

**User Story:** As a developer, I want to compare different model versions, so that I can track improvements and select the best performing model.

#### Acceptance Criteria

1. WHEN a new model is trained, THE Training_Pipeline SHALL save it with a version identifier (e.g., xgb_model_v3.pkl)
2. WHEN model comparison is requested, THE Training_Pipeline SHALL load multiple model versions and evaluate them on the same test set
3. WHEN models are compared, THE Training_Pipeline SHALL display accuracy, balanced accuracy, and per-class metrics for each version
4. WHEN the best model is identified, THE Training_Pipeline SHALL copy it to xgb_model_balanced.pkl as the production model
5. THE Training_Pipeline SHALL maintain a model performance history log with timestamps, metrics, and training parameters
6. THE Training_Pipeline SHALL generate a comparison report showing improvement over baseline
7. IF a new model performs worse than the current production model, THEN THE Training_Pipeline SHALL warn the user before replacing it

### Requirement 10: Data Quality Validation

**User Story:** As a data scientist, I want automated data quality checks, so that the model trains on clean and valid data.

#### Acceptance Criteria

1. WHEN data is loaded, THE Training_Pipeline SHALL check for missing values in all 11 required features
2. WHEN missing values are found, THE Training_Pipeline SHALL report which features and how many rows are affected
3. WHEN data ranges are validated, THE Training_Pipeline SHALL verify RSI is between 0-100, VIX is positive, and EMAs are reasonable
4. WHEN duplicate timestamps are detected, THE Training_Pipeline SHALL remove duplicates keeping the first occurrence
5. WHEN outcome labels are validated, THE Training_Pipeline SHALL verify all values are in the set {-1, 0, 1}
6. THE Training_Pipeline SHALL check for data leakage by ensuring no future data is used for past predictions
7. THE Training_Pipeline SHALL validate that test set contains at least 10 samples of each class for meaningful evaluation
8. IF data quality issues are found, THEN THE Training_Pipeline SHALL generate a detailed report and optionally halt training

### Requirement 11: Prediction Confidence Calibration

**User Story:** As a trader, I want calibrated confidence scores, so that a 70% confidence prediction is actually correct 70% of the time.

#### Acceptance Criteria

1. WHEN predictions are made, THE XGBoost_Model SHALL output probability distributions for all three classes
2. WHEN confidence is calculated, THE Prediction_Engine SHALL use the maximum probability as the base confidence
3. WHEN full agreement exists among all three models, THE Prediction_Engine SHALL boost confidence by 10 percentage points
4. WHEN models disagree, THE Prediction_Engine SHALL reduce confidence proportionally to the disagreement level
5. WHEN historical calibration data exists, THE Prediction_Engine SHALL adjust confidence based on historical accuracy at each confidence level
6. THE Prediction_Engine SHALL track actual accuracy for predictions made at each 10% confidence bucket (0-10%, 10-20%, etc.)
7. THE Prediction_Engine SHALL generate a calibration curve showing predicted confidence vs actual accuracy
8. FOR ALL predictions, the confidence score SHALL be between 0 and 100 (validity property)

### Requirement 12: Real-time Model Monitoring

**User Story:** As a system administrator, I want real-time model performance monitoring, so that I can detect model degradation and trigger retraining.

#### Acceptance Criteria

1. WHEN predictions are logged, THE Prediction_Engine SHALL track the running accuracy over the last 50 predictions
2. WHEN accuracy drops below 50%, THE Prediction_Engine SHALL generate a warning alert
3. WHEN accuracy drops below 40%, THE Prediction_Engine SHALL generate a critical alert and recommend immediate retraining
4. WHEN class distribution shifts, THE Prediction_Engine SHALL detect if recent predictions are biased toward one class (>60%)
5. THE Prediction_Engine SHALL calculate and display daily, weekly, and monthly accuracy trends
6. THE Prediction_Engine SHALL track prediction confidence distribution and alert if average confidence drops below 60%
7. THE Prediction_Engine SHALL monitor feature drift by comparing recent feature distributions to training data distributions
8. WHEN 100 new outcomes are collected, THE Prediction_Engine SHALL recommend retraining to incorporate new data

### Requirement 13: Backtesting Integration

**User Story:** As a trader, I want to backtest the improved model on historical data, so that I can validate performance before live trading.

#### Acceptance Criteria

1. WHEN backtesting is initiated, THE Training_Pipeline SHALL split data into training (first 60%), validation (next 20%), and test (last 20%) sets
2. WHEN backtesting runs, THE Training_Pipeline SHALL train on training set, tune on validation set, and report final metrics on test set
3. WHEN backtesting completes, THE Training_Pipeline SHALL generate a report showing accuracy progression over time
4. WHEN trading strategies are backtested, THE Scenario_Analyzer SHALL simulate trades based on model predictions and calculate P&L
5. THE Training_Pipeline SHALL calculate maximum drawdown, win rate, and average profit per trade
6. THE Training_Pipeline SHALL identify the best and worst performing time periods
7. THE Training_Pipeline SHALL compare backtested performance against buy-and-hold strategy

### Requirement 14: Configuration Management

**User Story:** As a developer, I want centralized configuration management, so that I can easily adjust model parameters and weights without code changes.

#### Acceptance Criteria

1. THE Training_Pipeline SHALL load all hyperparameters from a configuration file (config.yaml or config.json)
2. THE Prediction_Engine SHALL load consensus weights (XGBoost, Groq, Gemini) from the configuration file
3. THE Training_Pipeline SHALL load the sideways threshold from the configuration file
4. THE Training_Pipeline SHALL load SMOTE parameters (sampling_strategy, k_neighbors) from the configuration file
5. WHEN configuration is changed, THE Training_Pipeline SHALL validate all parameters are within acceptable ranges
6. THE Training_Pipeline SHALL log the active configuration at the start of each training run
7. THE Training_Pipeline SHALL support configuration profiles (development, production) for different environments

### Requirement 15: Documentation and Reporting

**User Story:** As a user, I want comprehensive documentation and automated reports, so that I can understand model behavior and make informed decisions.

#### Acceptance Criteria

1. WHEN training completes, THE Training_Pipeline SHALL generate a markdown report with all metrics, confusion matrix, and feature importance
2. WHEN scenario analysis runs, THE Scenario_Analyzer SHALL generate a markdown report with predictions, reasoning, and trading strategies
3. WHEN model comparison is performed, THE Training_Pipeline SHALL generate a comparison table showing all versions and their metrics
4. THE Training_Pipeline SHALL include visualizations (confusion matrix heatmap, feature importance bar chart, accuracy trends)
5. THE Training_Pipeline SHALL generate a summary section highlighting key findings and recommendations
6. THE Training_Pipeline SHALL include timestamps, data statistics, and reproducibility information in all reports
7. THE Training_Pipeline SHALL save all reports to a designated reports directory with timestamped filenames

