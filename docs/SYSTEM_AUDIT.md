# System Audit - Nifty AI Predictor
**Generated:** March 9, 2026  
**Purpose:** Complete documentation of all prediction engines and their interconnections

---

## 1. ENHANCED_PREDICTION_ENGINE.PY

### Purpose
Primary prediction engine using enhanced indicator scoring logic with state management. Implements 9 fixes for improved accuracy and time-aware predictions.

### Main Function
**`get_enhanced_prediction(price_data, indicator_summary, df_candles, oi_data, vix_data, news_data)`**
- Returns prediction dict or None if time filter blocks
- Applies time-of-day confidence multiplier
- Uses regime-based indicator weighting
- Maintains state between predictions for direction-based scoring

### All Functions

**`get_enhanced_prediction(...)`**
- Orchestrates entire prediction flow
- Applies time filter first (returns None if blocked)
- Calculates all indicator scores
- Applies regime-based weights
- Returns prediction with direction, confidence, reasons

**`initialize_previous_day_levels(df_candles)`**
- Extracts previous day high/low from historical data
- Called at system startup
- Updates prediction_state with support/resistance levels

### Indicators/Features Used
1. **RSI (14)** - Direction-aware scoring
2. **MACD** - Histogram momentum
3. **EMA (9, 21, 50)** - Crossover detection
4. **Bollinger Bands** - Position with trend context
5. **VIX** - Direction and rate of change
6. **Opening Range** - First 15min high/low breakout
7. **Previous Day Levels** - Support/resistance
8. **ADX** - Market regime detection (trending vs ranging)
9. **Time of Day** - Confidence multiplier

### Connections to Other Files
- **indicator_scoring.py** - All scoring functions and time filter
- **prediction_state.py** - State management for direction-based scoring
- **config.py** - Timezone settings

### Hardcoded Values/Thresholds
- **Strong Bullish:** final_score >= 1.5, confidence = min(85, 50 + score*10)
- **Moderate Bullish:** final_score >= 0.5, confidence = min(70, 45 + score*10)
- **Strong Bearish:** final_score <= -1.5, confidence = min(85, 50 + abs(score)*10)
- **Moderate Bearish:** final_score <= -0.5, confidence = min(70, 45 + abs(score)*10)
- **Sideways:** -0.5 < final_score < 0.5, confidence = 40
- **Opening Range Weight:** 0.15 (fixed)
- **Previous Day Weight:** 0.10 (fixed)

### Output Format
```python
{
    "direction": "BULLISH/BEARISH/SIDEWAYS",
    "confidence": 0-100,
    "strength": "WEAK/MODERATE/STRONG",
    "consensus": "ENHANCED_SCORING",
    "agreement": "<market_regime>",
    "top_3_reasons": [...],
    "one_line_summary": "...",
    "model_used": "Enhanced Indicator Scoring v2.0",
    "generated_at": "HH:MM:SS IST",
    "raw_score": float,
    "final_score": float,
    "time_multiplier": float,
    "market_regime": "TRENDING/RANGING/NEUTRAL",
    "indicator_weights": {...},
    "all_scores": {...}
}
```

---

## 2. INDICATOR_SCORING.PY

### Purpose
Core scoring logic for all technical indicators. Implements 9 fixes for improved prediction accuracy.

### All Functions

**`get_time_confidence_multiplier(hour, minute)`**
- Returns confidence multiplier based on time of day
- Returns None to skip prediction during disabled zones
- Used by: enhanced_prediction_engine.py, standalone_logger_v2.py

**`score_rsi(current_rsi, previous_rsi)`**
- Scores RSI with direction awareness
- Considers both level and momentum
- Returns: -2 to +2

**`score_macd(macd_value, macd_signal, prev_macd_value, prev_macd_signal)`**
- Scores MACD using histogram momentum
- Detects strengthening vs weakening trends
- Returns: -2 to +2

**`score_ema(price, ema9, ema21, ema50, prev_ema9, prev_ema21)`**
- Scores EMA with golden/death cross detection
- Combines trend structure with crossover signals
- Returns: -3 to +3 (capped)

**`score_bollinger(price, bb_position, ema9, ema21)`**
- Scores Bollinger Bands with trend awareness
- Near upper band in uptrend = bullish continuation
- Near upper band in downtrend = bearish resistance
- Returns: -2 to +2

**`score_vix(current_vix, previous_vix)`**
- Scores VIX based on direction and rate of change
- VIX direction matters more than level
- Returns: -3 to +3

**`get_market_regime(high, low, close)`**
- Detects if market is trending or ranging using ADX
- Returns: 'TRENDING', 'RANGING', or 'NEUTRAL'

**`get_indicator_weights(regime)`**
- Adjusts indicator weights based on market regime
- Trending: favor MACD/EMA
- Ranging: favor RSI/BB
- Returns: dict of weights

**`update_opening_range(price, hour, minute)`**
- Tracks high/low of first 15 mins after 9:30
- Called on every price update during 9:30-9:45

**`score_opening_range(price)`**
- Scores based on opening range breakout
- Returns: -2 to +2

**`reset_opening_range()`**
- Resets opening range at start of new day
- Called at 9:15 AM daily

**`score_previous_day_levels(price, prev_day_high, prev_day_low)`**
- Scores based on previous day high/low levels
- Key support/resistance levels
- Returns: -2 to +2

### Indicators/Features Used
- RSI (14 period)
- MACD (12, 26, 9)
- EMA (9, 21, 50)
- Bollinger Bands (20 period, 2 std)
- ATR (14 period)
- VIX (India VIX)
- ADX (14 period) - for regime detection
- Opening Range (9:30-9:45 high/low)
- Previous Day High/Low

### Connections to Other Files
- **enhanced_prediction_engine.py** - Imports all scoring functions
- **prediction_state.py** - Uses global opening_range state
- **trade_signal_scanner.py** - Uses time filter

### Hardcoded Values/Thresholds

**Time Filter:**
- Before 9:15 AM → None (market closed)
- 9:15-9:30 AM → None (pre-open, no real data)
- 9:30-10:00 AM → 0.5x (opening volatile)
- 10:00-12:00 PM → 1.0x (prime trading)
- 12:00-13:30 PM → 0.6x (lunch, lower volume)
- 13:30-14:30 PM → 1.0x (prime afternoon)
- 14:30-15:25 PM → 0.7x (pre-close volatility)
- After 15:25 PM → None (post-close, stale data)

**RSI Thresholds:**
- Oversold: < 30
- Overbought: > 70
- Neutral: 40-60

**VIX Change Thresholds:**
- Spiking fast: > 5% change
- Rising: > 2% change
- Dropping fast: < -5% change
- Falling: < -2% change

**ADX Regime Thresholds:**
- Trending: ADX > 25
- Ranging: ADX < 20
- Neutral: 20 <= ADX <= 25

**Indicator Weights by Regime:**

TRENDING:
- RSI: 0.10, MACD: 0.30, EMA: 0.30, BB: 0.05, VIX: 0.15, Global: 0.10

RANGING:
- RSI: 0.30, MACD: 0.10, EMA: 0.10, BB: 0.30, VIX: 0.10, Global: 0.10

NEUTRAL:
- RSI: 0.20, MACD: 0.20, EMA: 0.20, BB: 0.10, VIX: 0.15, Global: 0.15

**Bollinger Band Position:**
- Near upper: > 0.8
- Near lower: < 0.2
- Middle: 0.2-0.8

**Opening Range:**
- Establishment period: 9:30-9:45 AM (15 minutes)
- Breakout: price > opening_high or price < opening_low

**Previous Day Levels:**
- Near high: within 10% of range from top
- Near low: within 10% of range from bottom

---

## 3. TRADE_SIGNAL_SCANNER.PY

### Purpose
Scans for CALL and PUT option trade setups based on strict verified backtest rules. Locked rules with 50% win rate and +50 points profit.

### Main Function
**`scan_for_signals(candle_data)`**
- Scans current market data for trade signals
- Returns signal dict or NO_TRADE
- Requires 20+ candles minimum

### All Functions

**`calculate_rsi(prices, period=14)`**
- Calculates RSI indicator
- Standard RSI formula

**`calculate_atr(high, low, close, period=14)`**
- Calculates Average True Range
- Uses true range (max of 3 calculations)

**`generate_trade_signal(...)`**
- Core signal generation logic
- Checks CALL and PUT setups
- Validates confluence score (7/7 required)
- Returns detailed trade setup or NO_TRADE

**`scan_for_signals(candle_data)`**
- Wrapper function
- Calculates indicators
- Calls generate_trade_signal
- Returns final signal

### Indicators/Features Used
- RSI (14 period)
- ATR (14 period)
- Recent High/Low (20 candles)
- Position in Range
- Distance to Support/Resistance
- Rally Size
- Candles Since Low
- Time of Day Filter

### Connections to Other Files
- **app.py** - Called for trade signal display
- **indicators.py** - Uses calculate_rsi, calculate_atr
- Standalone module (no imports from other prediction engines)

### Hardcoded Values/Thresholds

**CALL Setup (7/7 confluence required):**
1. Position < 0.25 (near support)
2. RSI < 45 (oversold)
3. RSI rising (momentum building)
4. Distance to support < 25 points
5. R:R > 2.0 (risk/reward ratio)
6. Candles since low > 3 (consolidation)
7. Time filter: 10:00-12:00 or 13:30-14:30

**PUT Setup (7/7 confluence required):**
1. Position > 0.7 (near resistance)
2. RSI > 60 (overbought)
3. Distance to resistance < 5 points
4. Distance to support > 100 points (big rally)
5. Rally size > 80 points
6. R:R > 2.0 (risk/reward ratio)
7. Time filter: 10:00-12:00 or 13:30-14:30

**Stop Loss Calculation:**
- ATR-based: recent_low/high ± (ATR * 0.5)
- Minimum stop distance: max(ATR * 0.3, 5 points)
- Minimum risk: 5 points

**Target Calculation:**
- Target 1: entry ± (ATR * 1.0)
- Target 2: entry ± (ATR * 1.5)

**Time Filter:**
- High confidence zones: 10:00-12:00 PM or 13:30-14:30 PM
- Outside these zones: NO_TRADE

**Breakout Protection (PUT):**
- If price > recent_high + 10 → NO_TRADE (breakout detected)

---

## 4. XGB_MODEL.PY

### Purpose
XGBoost machine learning model for Nifty prediction. Trains on logged predictions and actual outcomes using raw indicator values.

### Main Functions

**`train_model(log_path='prediction_log.csv')`**
- Trains XGBoost classifier on historical data
- Requires minimum 300 samples
- Uses 80/20 train/test split (no shuffle for time series)
- Saves model to xgb_model.pkl
- Returns training metrics

**`load_model()`**
- Loads trained model from disk
- Returns model object or None

**`predict(indicator_values)`**
- Makes prediction using trained model
- Returns (direction, confidence) tuple
- direction: 1 (UP), -1 (DOWN), 0 (SIDEWAYS)
- confidence: 0-100 (max probability * 100)

**`get_model_info()`**
- Returns model metadata
- File size, last modified, hyperparameters

### Features Used (11 total)
1. rsi_14 - RSI indicator
2. macd_value - MACD line
3. macd_signal - MACD signal line
4. ema_9 - 9-period EMA
5. ema_21 - 21-period EMA
6. ema_50 - 50-period EMA
7. bb_position - Bollinger Band position (0-1)
8. atr_14 - Average True Range
9. vix - India VIX
10. day_of_week - 0=Monday, 4=Friday
11. us_market_change - S&P 500 % change

**Note:** PCR removed - APIs unreliable

### Connections to Other Files
- **prediction_log.csv** - Training data source
- **ai_engine_consensus.py** - Called for XGBoost predictions
- **prediction_logger.py** - Uses extract_indicator_values function

### Hardcoded Values/Thresholds

**Model Hyperparameters:**
- n_estimators: 200
- max_depth: 4
- learning_rate: 0.05
- subsample: 0.8
- colsample_bytree: 0.8
- eval_metric: 'mlogloss'
- random_state: 42

**Training Requirements:**
- MIN_SAMPLES: 300 (minimum samples to train)
- Test size: 20% (0.2)
- Shuffle: False (preserve time series order)

**Class Mapping:**
- -1 (DOWN) → 0 (XGBoost class)
- 0 (SIDEWAYS) → 1 (XGBoost class)
- 1 (UP) → 2 (XGBoost class)

**Model Path:**
- MODEL_PATH: 'xgb_model.pkl'

---

## 5. AI_ENGINE_CONSENSUS.PY

### Purpose
Dual-AI consensus prediction engine using Groq (Llama 3.3 70B) and Gemini (2.5 Flash). Integrates XGBoost ML model with LLM analysis for weighted consensus.

### Main Function
**`get_consensus_prediction(...)`**
- Primary entry point for AI-based predictions
- Hierarchy: XGBoost (60%) + Groq (20%) + Gemini (20%)
- Falls back to Dual-AI (50/50) if XGBoost unavailable
- Calls both LLMs in parallel using ThreadPoolExecutor

### All Functions

**`_build_analysis_prompt(...)`**
- Builds comprehensive prompt for LLM analysis
- Includes all market data, indicators, news, global cues
- Formats data for AI consumption
- Returns formatted prompt string

**`_call_groq_api(prompt)`**
- Calls Groq API (Llama 3.3 70B)
- Handles JSON parsing and errors
- Records API usage
- Returns prediction dict

**`_call_gemini_api(prompt)`**
- Calls Gemini API (Gemini 2.5 Flash)
- Uses new google-genai package
- Forces JSON response with response_mime_type
- Returns prediction dict

**`_calculate_consensus(groq_pred, gemini_pred)`**
- Calculates consensus between two LLM predictions
- Handles agreement levels (FULL/PARTIAL/CONFLICTING)
- Merges price targets and reasons
- Returns consensus dict

**`_calculate_xgb_consensus(xgb_direction, xgb_confidence, groq_pred, gemini_pred)`**
- Calculates weighted consensus with XGBoost (60%) + LLMs (40%)
- Uses voting system with weights
- Adjusts confidence based on agreement level
- Returns consensus dict

**`_direction_to_text(direction)`**
- Converts numeric direction to text
- 1 → "BULLISH", -1 → "BEARISH", 0 → "SIDEWAYS"

**`_text_to_direction(text)`**
- Converts text direction to numeric
- "BULLISH" → 1, "BEARISH" → -1, "SIDEWAYS" → 0

**`_extract_xgb_features(indicator_summary, oi_data, vix_data, global_cues)`**
- Extracts raw indicator values for XGBoost
- Converts indicator_summary to XGBoost feature dict
- Calculates derived features (bb_position, us_market_change)
- Returns feature dict

**`get_rule_based_prediction(indicator_summary, oi_data, vix_data, news)`**
- Fallback rule-based prediction when both AIs fail
- Simple scoring system
- Returns basic prediction dict

### Indicators/Features Used
All indicators from indicator_summary:
- RSI, MACD, EMA, Bollinger Bands, ATR, VIX
- PCR, Max Pain, Support/Resistance
- News sentiment
- Global market cues
- Candlestick patterns

### Connections to Other Files
- **config.py** - API keys and model names
- **xgb_model.py** - XGBoost predictions
- **prediction_logger.py** - extract_indicator_values function
- **groq** package - Llama 3.3 70B API
- **google.genai** package - Gemini 2.5 Flash API

### Hardcoded Values/Thresholds

**Consensus Weights:**
- XGBoost: 60% (if available)
- Groq: 20%
- Gemini: 20%
- Fallback (no XGBoost): Groq 50%, Gemini 50%

**Agreement Levels:**
- FULL: All 3 agree → confidence + 10
- PARTIAL: XGBoost agrees with final → no adjustment
- CONFLICTING: XGBoost disagrees → confidence - 15

**Confidence Caps:**
- Maximum: 95
- Minimum: 30

**LLM API Settings:**
- Groq temperature: 0.2
- Groq max_tokens: 1500
- Gemini temperature: 0.2
- Gemini max_tokens: 1500
- Gemini response_mime_type: 'application/json'

**Rule-Based Scoring (Fallback):**
- Strong signal: score >= 3 or <= -3
- Moderate signal: score >= 1 or <= -1
- Sideways: -1 < score < 1
- PCR bullish: > 1.2
- PCR bearish: < 0.8
- News bullish: score > 0.2
- News bearish: score < -0.2

---

## SYSTEM FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA COLLECTION                          │
│  (data_fetcher.py)                                          │
│  - NSE API (price, candles)                                 │
│  - yfinance (VIX, global cues)                              │
│  - Angel One (options chain) [optional]                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              INDICATOR CALCULATION                          │
│  (indicators.py)                                            │
│  - RSI, MACD, EMA, BB, ATR                                  │
│  - Returns indicator_summary dict                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 PREDICTION ENGINES                          │
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │  1. ENHANCED PREDICTION ENGINE               │          │
│  │     (enhanced_prediction_engine.py)          │          │
│  │     - Time filter check                      │          │
│  │     - Indicator scoring (9 fixes)            │          │
│  │     - Regime-based weighting                 │          │
│  │     - State management                       │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │  2. AI ENGINE CONSENSUS                      │          │
│  │     (ai_engine_consensus.py)                 │          │
│  │     - XGBoost ML (60% weight)                │          │
│  │     - Groq Llama 3.3 70B (20% weight)        │          │
│  │     - Gemini 2.5 Flash (20% weight)          │          │
│  │     - Weighted consensus                     │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │  3. TRADE SIGNAL SCANNER                     │          │
│  │     (trade_signal_scanner.py)                │          │
│  │     - CALL setup (7/7 confluence)            │          │
│  │     - PUT setup (7/7 confluence)             │          │
│  │     - ATR-based stops/targets                │          │
│  └──────────────────────────────────────────────┘          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   PREDICTION OUTPUT                         │
│  {                                                          │
│    "direction": "BULLISH/BEARISH/SIDEWAYS",                │
│    "confidence": 0-100,                                     │
│    "strength": "WEAK/MODERATE/STRONG",                     │
│    "top_3_reasons": [...],                                  │
│    "model_used": "...",                                     │
│    ...                                                      │
│  }                                                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA LOGGING                             │
│  (prediction_logger_v2.py)                                  │
│  - Writes to predictions_v2.csv                             │
│  - Writes to predictions_v2_YYYY_MM_DD.csv                  │
│  - 17 columns with all indicators                           │
│  - QUOTE_ALL, UTF-8 encoding                                │
└─────────────────────────────────────────────────────────────┘
```

---

## PREDICTION ENGINE COMPARISON

| Feature | Enhanced Engine | AI Consensus | Trade Scanner |
|---------|----------------|--------------|---------------|
| **Type** | Rule-based scoring | ML + LLM hybrid | Pattern-based |
| **Speed** | Fast (~1 sec) | Slow (~3-5 sec) | Fast (~1 sec) |
| **Output** | Direction + confidence | Direction + confidence + targets | Trade setup or NO_TRADE |
| **Use Case** | Minute-by-minute logging | Dashboard display | Options trading signals |
| **Time Filter** | Yes (integrated) | No (external) | Yes (integrated) |
| **State Management** | Yes (direction-aware) | No | No |
| **Regime Detection** | Yes (ADX-based) | No | No |
| **ML Model** | No | Yes (XGBoost 60%) | No |
| **LLM Analysis** | No | Yes (Groq + Gemini) | No |
| **Confidence Range** | 40-85 | 30-95 | 70-95 |
| **Fallback** | None (always works) | Rule-based | NO_TRADE |

---

## DATA FLOW FOR LOGGER V2

```
1. standalone_logger_v2.py (main loop)
   ↓
2. Check is_market_open() → 9:15-15:30 PM
   ↓
3. get_time_confidence_multiplier() → returns multiplier or None
   ↓
4. If None → skip this minute
   ↓
5. If multiplier exists → fetch data
   ↓
6. data_fetcher.py → get_live_nifty_price(), get_candle_data(), etc.
   ↓
7. indicators.py → calculate_all_indicators(), get_indicator_summary()
   ↓
8. enhanced_prediction_engine.py → get_enhanced_prediction()
   ↓
9. indicator_scoring.py → score_rsi(), score_macd(), etc.
   ↓
10. Apply time_multiplier to confidence
   ↓
11. prediction_logger_v2.py → log_prediction()
   ↓
12. Write to predictions_v2.csv (main)
   ↓
13. Write to predictions_v2_YYYY_MM_DD.csv (daily backup)
```

---

## CRITICAL DEPENDENCIES

### Enhanced Prediction Engine depends on:
- indicator_scoring.py (all scoring functions)
- prediction_state.py (state management)
- config.py (timezone)

### AI Engine Consensus depends on:
- xgb_model.py (ML predictions)
- config.py (API keys, model names)
- groq package (Llama API)
- google.genai package (Gemini API)

### Trade Signal Scanner depends on:
- pandas_ta or custom RSI/ATR calculations
- No external prediction engines (standalone)

### XGBoost Model depends on:
- prediction_log.csv (training data)
- xgboost package
- sklearn (train/test split, metrics)
- pickle (model serialization)

---

## CONFIGURATION SOURCES

All hardcoded values should eventually be moved to config.py:

**Currently in config.py:**
- Market hours (9:15-15:30)
- EMA periods (9, 21, 50, 200)
- RSI period (14)
- MACD periods (12, 26, 9)
- BB period (20, 2 std)
- ATR period (14)
- VIX thresholds (13 low, 20 high)
- PCR thresholds (1.2 bullish, 0.8 bearish)

**Still hardcoded in files:**
- Time filter multipliers (indicator_scoring.py)
- Indicator weights by regime (indicator_scoring.py)
- Trade setup confluence rules (trade_signal_scanner.py)
- XGBoost hyperparameters (xgb_model.py)
- Consensus weights (ai_engine_consensus.py)

---

## KNOWN ISSUES & LIMITATIONS

1. **PCR Data Unreliable** - Removed from XGBoost features due to API failures
2. **Options Chain Failures** - Angel One and NSE options APIs frequently fail
3. **XGBoost Requires 300+ Samples** - Cannot train until enough data collected
4. **No Real-Time Backtesting** - Outcomes filled after 15 minutes, not real-time
5. **State Reset on Restart** - prediction_state lost if logger crashes
6. **No Multi-Timeframe Analysis** - Only uses 5-minute candles
7. **Global Cues May Be Stale** - US market data not always real-time
8. **News Sentiment Not Integrated** - Collected but not used in scoring

---

## FUTURE ENHANCEMENTS

1. **Move all thresholds to config.py** - Centralize configuration
2. **Add XGBoost retraining schedule** - Weekly automatic retraining
3. **Implement real-time outcome checking** - Update outcomes as they happen
4. **Add multi-timeframe analysis** - 1min, 5min, 15min candles
5. **Persist prediction_state** - Save state to disk for crash recovery
6. **Add model versioning** - Track model performance over time
7. **Implement A/B testing** - Compare different scoring strategies
8. **Add confidence calibration** - Adjust confidence based on historical accuracy
9. **Integrate news sentiment** - Add news scoring to enhanced engine
10. **Add volatility forecasting** - Predict VIX changes

---

**Last Updated:** March 9, 2026  
**Version:** 2.0 (Logger V2 with enhanced scoring)
