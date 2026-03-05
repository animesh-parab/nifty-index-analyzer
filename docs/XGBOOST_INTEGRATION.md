# XGBoost ML Model Integration

## Overview

The XGBoost ML model has been integrated as the **primary prediction layer** (60% weight) with Groq and Gemini LLMs as fallback/validation (20% each).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PREDICTION PIPELINE                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. XGBoost ML Model (60% weight)                          │
│     ├─ Trained on historical predictions + outcomes         │
│     ├─ Uses 13 raw indicator features                       │
│     └─ Returns: direction (1/-1/0) + confidence (0-100)     │
│                                                              │
│  2. Groq LLM (20% weight)                                   │
│     ├─ Llama 3.3 70B model                                  │
│     ├─ Real-time market analysis                            │
│     └─ Returns: BULLISH/BEARISH/SIDEWAYS + confidence       │
│                                                              │
│  3. Gemini LLM (20% weight)                                 │
│     ├─ Gemini 2.5 Flash model                               │
│     ├─ Real-time market analysis                            │
│     └─ Returns: BULLISH/BEARISH/SIDEWAYS + confidence       │
│                                                              │
│  ► WEIGHTED CONSENSUS                                        │
│     ├─ All agree → STRONG consensus (+10% confidence)       │
│     ├─ XGB agrees with final → MODERATE consensus           │
│     └─ XGB disagrees → WEAK consensus (-15% confidence)     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Features Used (13 Total)

The XGBoost model uses **raw indicator values** (NOT +1/-1 scores):

### Technical Indicators (8)
1. `rsi_14` - RSI (14 period)
2. `macd_value` - MACD line value
3. `macd_signal` - MACD signal line
4. `ema_9` - 9-period EMA
5. `ema_21` - 21-period EMA
6. `ema_50` - 50-period EMA
7. `bb_position` - Bollinger Band position (0-1)
8. `atr_14` - Average True Range (14 period)

### Market Indicators (3)
9. `pcr` - Put-Call Ratio
10. `vix` - India VIX
11. `us_market_change` - Average US market change %

### Time Features (2)
12. `hour` - Hour of day (9-15)
13. `day_of_week` - Day of week (0-4)

## Training Process

### 1. Data Collection (Automatic)

Every prediction is logged with:
- All 13 indicator values
- Prediction direction and confidence
- Entry price
- Timestamp

After 15 minutes, the system checks actual outcome:
- `1` = Price went UP (>0.1%)
- `-1` = Price went DOWN (>0.1%)
- `0` = Price stayed SIDEWAYS (±0.1%)

### 2. Training Requirements

- **Minimum samples**: 300 predictions with outcomes
- **Train/test split**: 80/20
- **Shuffle**: FALSE (time series data - order matters!)

### 3. Model Configuration

```python
XGBClassifier(
    n_estimators=200,      # 200 trees
    max_depth=4,           # Max tree depth
    learning_rate=0.05,    # Learning rate
    subsample=0.8,         # 80% data per tree
    colsample_bytree=0.8,  # 80% features per tree
    eval_metric='mlogloss' # Multi-class log loss
)
```

### 4. Training Metrics

After training, you'll see:
- **Accuracy**: Overall prediction accuracy
- **Class distribution**: UP/DOWN/SIDEWAYS counts
- **Confusion matrix**: Detailed prediction breakdown
- **Top features**: Most important indicators
- **Classification report**: Precision, recall, F1-score per class

## Usage

### Dashboard Integration

The XGBoost model is automatically used if `xgb_model.pkl` exists:

1. **During market hours**: Predictions are logged automatically
2. **After 300+ samples**: Retrain button becomes active
3. **After training**: Model is used for all predictions

### Manual Training

In the sidebar:
1. Navigate to "🤖 XGBoost ML Model" section
2. Check "Logged" and "With Outcome" counts
3. Wait until "Ready to train" shows ✅
4. Click "🔄 Retrain XGBoost Model"
5. View accuracy and top features

### Fallback Behavior

If XGBoost model doesn't exist:
- System falls back to Dual-AI consensus (50/50 Groq/Gemini)
- No functionality is lost
- Model can be trained anytime

## Files

### Core Files
- `xgb_model.py` - XGBoost model training and prediction
- `prediction_logger.py` - Logs predictions and outcomes
- `ai_engine_consensus.py` - Weighted consensus logic
- `app.py` - Dashboard with retrain button

### Data Files
- `prediction_log.csv` - Training data (auto-generated)
- `xgb_model.pkl` - Trained model (created after training)

## Monitoring

### Log Statistics

Check sidebar for:
- **Logged**: Total predictions logged
- **With Outcome**: Predictions with verified outcomes
- **Ready for training**: Whether 300+ samples available

### Model Information

After training:
- **Last updated**: When model was last trained
- **Size**: Model file size
- **Accuracy**: Test set accuracy
- **Top features**: Most important indicators

## Best Practices

### 1. Data Collection
- Let system run during market hours to collect data
- Need at least 300 samples before first training
- More data = better model (aim for 1000+ samples)

### 2. Retraining Schedule
- Retrain weekly (every Sunday after market close)
- Retrain after major market events
- Retrain when accuracy drops below 55%

### 3. Monitoring
- Check accuracy after each training
- Monitor class distribution (should be balanced)
- Review top features (should make sense)

### 4. Troubleshooting

**Problem**: Not enough data
- **Solution**: Wait for more predictions to be logged

**Problem**: Low accuracy (<50%)
- **Solution**: Collect more data, check feature quality

**Problem**: Model not loading
- **Solution**: Retrain model, check file permissions

**Problem**: Predictions seem wrong
- **Solution**: Check if model is stale, retrain with recent data

## Technical Details

### Time Series Considerations

- **No shuffling**: Data split preserves time order
- **No look-ahead bias**: Features only use past data
- **Outcome delay**: 15 minutes to verify prediction

### Feature Engineering

- **Raw values**: Uses actual indicator values, not signals
- **Normalization**: XGBoost handles different scales automatically
- **Missing values**: Handled with defaults (e.g., PCR=1.0, VIX=15.0)

### Prediction Flow

```python
# 1. Extract features
indicator_values = extract_indicator_values(df_candles, oi_data, vix_data, global_cues)

# 2. XGBoost prediction
xgb_direction, xgb_confidence = xgb_predict(indicator_values)

# 3. LLM predictions (parallel)
groq_pred = call_groq_api(prompt)
gemini_pred = call_gemini_api(prompt)

# 4. Weighted consensus
final_prediction = calculate_xgb_consensus(
    xgb_direction, xgb_confidence,  # 60%
    groq_pred, gemini_pred          # 20% + 20%
)
```

## Performance Expectations

### Initial Training (300 samples)
- Accuracy: 50-60%
- Confidence: Moderate
- Recommendation: Collect more data

### After 1000 samples
- Accuracy: 55-65%
- Confidence: Good
- Recommendation: Regular retraining

### After 5000+ samples
- Accuracy: 60-70%
- Confidence: High
- Recommendation: Weekly retraining

## Advantages

1. **Data-driven**: Learns from actual market outcomes
2. **Adaptive**: Improves with more data
3. **Fast**: Predictions in milliseconds
4. **Transparent**: Feature importance shows what matters
5. **Fallback**: LLMs provide validation and backup

## Limitations

1. **Needs data**: Requires 300+ samples to start
2. **Market changes**: Needs retraining as market evolves
3. **Not magic**: Can't predict black swan events
4. **Time lag**: 15-minute outcome delay for training

## Next Steps

1. **Install dependencies**: `pip install xgboost scikit-learn`
2. **Run dashboard**: Let it collect data during market hours
3. **Wait for 300+ samples**: Check sidebar for progress
4. **Train model**: Click retrain button when ready
5. **Monitor performance**: Check accuracy and retrain regularly

## Support

For issues or questions:
1. Check logs in terminal
2. Verify `prediction_log.csv` exists and has data
3. Ensure XGBoost and scikit-learn are installed
4. Check file permissions for `xgb_model.pkl`
