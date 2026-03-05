# 🔍 How Backtesting Works - Detailed Explanation

## 📊 Overview

Your backtesting engine tests AI predictions against **real historical price data** to see how well the model would have performed in the past.

---

## 🎯 Step-by-Step Process

### Step 1: Fetch Historical Data

**Source**: yfinance (Yahoo Finance)
**Data**: Real Nifty 50 / Bank Nifty historical prices

```python
# When you run backtest with:
# - Days: 7
# - Interval: 15m
# - Prediction: 30min

# It fetches:
ticker = yf.Ticker("^NSEI")  # Nifty 50
df = ticker.history(period="7d", interval="15m")

# This gives you:
# - Last 7 days of data
# - 15-minute candles
# - OHLCV (Open, High, Low, Close, Volume)
# - ~525 candles (7 days × 75 candles per day)
```

**Example Data**:
```
Date/Time           Open      High      Low       Close     Volume
2024-02-21 09:15   25000.0   25050.0   24990.0   25030.0   1000000
2024-02-21 09:30   25030.0   25080.0   25020.0   25070.0   1200000
2024-02-21 09:45   25070.0   25100.0   25060.0   25090.0   1100000
... (525 more candles)
```

---

### Step 2: Calculate Technical Indicators

For each candle, calculate:
- **RSI** (14 periods)
- **MACD** (12, 26, 9)
- **EMA** (9, 21, 50, 200)
- **Bollinger Bands**
- **ATR**
- **VWAP**
- **Supertrend**

**Example**:
```
Date/Time           Close     RSI    MACD   EMA9    EMA21
2024-02-21 09:15   25030.0   52.3   -5.2   25020   25010
2024-02-21 09:30   25070.0   58.1   +2.1   25035   25015
2024-02-21 09:45   25090.0   61.4   +8.5   25048   25022
```

---

### Step 3: Walk Through History (Time Travel)

**This is the KEY part!**

The backtesting engine "walks through" history, candle by candle, **as if it's happening in real-time**.

```
For each candle (i = 0 to 525):
    1. Look at data UP TO candle i (no future data!)
    2. Generate prediction based on indicators
    3. Wait for actual outcome (candle i + prediction_timeframe)
    4. Compare prediction vs actual result
    5. Calculate profit/loss
```

**Example Timeline**:
```
09:15 AM - Current candle
         ↓
    [Generate Prediction]
    Based on: RSI, MACD, EMA, etc.
    Prediction: BULLISH (confidence 65%)
         ↓
09:45 AM - 30 minutes later (prediction timeframe)
         ↓
    [Check Actual Result]
    Price went from 25030 → 25090 (+60 points)
    Prediction was CORRECT! ✓
         ↓
    [Calculate P&L]
    Position size: ₹6,500 (65% confidence × 10% capital)
    Profit: ₹6,500 × (60/25030) = ₹15.60
```

---

### Step 4: Generate Prediction (No Future Data!)

**CRITICAL**: At each point, the model only sees data **up to that moment**.

```python
# At 09:15 AM, model sees:
historical_df = df.iloc[:current_index+1]  # Only past data!

# Calculate indicators from past data
indicator_summary = get_indicator_summary(historical_df)

# Generate prediction
prediction = get_rule_based_prediction(
    indicator_summary,  # RSI, MACD, EMA from past
    oi_data,           # Mock data (not available historically)
    vix_data,          # Mock data
    news_sentiment     # Mock data
)

# Returns:
# {
#   'direction': 'BULLISH',
#   'confidence': 65,
#   'strength': 'MODERATE'
# }
```

**What's Used**:
- ✅ Historical prices (up to current candle)
- ✅ Technical indicators (calculated from past)
- ⚠️ Options data (mocked - not available historically)
- ⚠️ VIX (mocked - set to 15.0)
- ⚠️ News sentiment (mocked - set to neutral)

---

### Step 5: Check Actual Outcome

After prediction timeframe (e.g., 30 minutes), check what actually happened:

```python
# Current candle (09:15 AM)
entry_price = 25030.0

# Future candle (09:45 AM - 30 min later)
exit_price = 25090.0

# Calculate actual move
actual_move = ((exit_price - entry_price) / entry_price) × 100
# = ((25090 - 25030) / 25030) × 100
# = +0.24%

# Was prediction correct?
if prediction == 'BULLISH' and actual_move > 0:
    correct = True  ✓
```

---

### Step 6: Simulate Trade

Calculate profit/loss as if you actually traded:

```python
# Position sizing based on confidence
position_size = capital × (confidence / 100) × 0.1
# = 100,000 × (65 / 100) × 0.1
# = ₹6,500

# For BULLISH prediction (Long position)
quantity = position_size / entry_price
# = 6,500 / 25030
# = 0.26 lots

# Profit/Loss
pnl = quantity × (exit_price - entry_price)
# = 0.26 × (25090 - 25030)
# = 0.26 × 60
# = ₹15.60

# Update capital
capital = 100,000 + 15.60 = 100,015.60
```

---

### Step 7: Repeat for All Candles

Do this for **every candle** in the historical data:

```
Candle 1 (09:15) → Predict → Wait 30min → Check → P&L: +₹15
Candle 2 (09:30) → Predict → Wait 30min → Check → P&L: -₹8
Candle 3 (09:45) → Predict → Wait 30min → Check → P&L: +₹12
...
Candle 525 (Day 7, 15:30) → Final result
```

**Total**: 465 predictions (some candles skipped due to timeframe)

---

## 📊 What Data Is Actually Used?

### Real Historical Data ✅
1. **Price Data** (OHLCV)
   - Source: yfinance
   - Period: Last 7-60 days
   - Interval: 5m, 15m, 30m, 1h, or 1d
   - **100% Real**: Actual Nifty prices from NSE

2. **Technical Indicators**
   - Calculated from real prices
   - RSI, MACD, EMA, BB, ATR, VWAP
   - **100% Real**: Based on actual price movements

### Mocked Data ⚠️
1. **Options Chain**
   - PCR set to 1.0 (neutral)
   - Max Pain = current price
   - **Not Real**: Historical options data not available

2. **VIX**
   - Set to 15.0 (average)
   - **Not Real**: Could fetch real VIX history but not implemented

3. **News Sentiment**
   - Set to 0 (neutral)
   - **Not Real**: Historical news not available

---

## 🎯 Why This Approach?

### Advantages ✅
1. **Tests Core Logic**: Technical indicators are the main prediction drivers
2. **Fast**: No need to fetch options/news data
3. **Reliable**: Price data is accurate and complete
4. **Fair**: No look-ahead bias (only uses past data)

### Limitations ⚠️
1. **Missing Options Data**: Real PCR/OI could improve accuracy
2. **Missing VIX**: Real volatility data could help
3. **Missing News**: Sentiment could affect predictions
4. **Simplified**: Real trading has slippage, fees, etc.

---

## 📈 Example: Your 56.3% Win Rate Test

**Configuration**:
- Days: 7
- Interval: 15m
- Prediction: 30min
- Capital: ₹100,000

**What Happened**:
```
1. Fetched 7 days of Nifty data (525 candles)
2. Calculated indicators for each candle
3. Generated 465 predictions
4. Checked actual outcomes
5. Simulated trades

Results:
- 262 correct predictions (56.3%)
- 203 incorrect predictions (43.7%)
- Final capital: ₹100,110 (+₹110)
- Bullish accuracy: 48.0%
- Bearish accuracy: 61.5%
```

---

## 🔍 How to Verify It's Working Correctly

### Test 1: Check Data Range
```python
# In backtesting_engine.py, add print:
print(f"Data range: {df.index[0]} to {df.index[-1]}")
print(f"Total candles: {len(df)}")
```

### Test 2: Check Predictions
```python
# Print first few predictions:
for i in range(5):
    print(f"Candle {i}: {prediction['direction']} ({prediction['confidence']}%)")
```

### Test 3: Verify No Future Data
```python
# Ensure only past data is used:
historical_df = df.iloc[:index+1]  # ✓ Correct
# NOT: df.iloc[:]  # ✗ Would use future data
```

---

## 💡 Improving Backtesting Accuracy

### Option 1: Add Real VIX Data
```python
# Fetch historical VIX
vix_ticker = yf.Ticker("^INDIAVIX")
vix_history = vix_ticker.history(period="7d", interval="15m")

# Use real VIX instead of mocked 15.0
vix_data = {'vix': vix_history['Close'].iloc[index]}
```

### Option 2: Add Real Options Data (Complex)
- Would need historical options chain data
- Not easily available for free
- Angel One doesn't provide historical OI

### Option 3: Add News Sentiment (Complex)
- Would need historical news data
- Sentiment analysis on past news
- Time-consuming to implement

---

## 🎯 Bottom Line

**Your backtesting is using**:
- ✅ **Real Nifty prices** from the last 7-60 days
- ✅ **Real technical indicators** calculated from those prices
- ⚠️ **Mocked options/VIX/news** data (set to neutral)

**This is GOOD because**:
- Technical indicators are your main prediction drivers (80% weight)
- Options/VIX/news are secondary (20% weight)
- Results are reliable for testing indicator-based strategies

**To improve**:
1. Optimize indicator parameters (what you're doing now)
2. Add real VIX data (easy to implement)
3. Test longer periods (30-60 days)
4. Implement stop loss/take profit

---

## 📊 Data Flow Diagram

```
yfinance API
    ↓
[Fetch 7 days of Nifty data]
    ↓
[525 candles with OHLCV]
    ↓
[Calculate Indicators]
    ↓
[Walk through each candle]
    ↓
For each candle:
    ├─ Use only past data
    ├─ Generate prediction (RSI, MACD, EMA)
    ├─ Wait for outcome (30 min later)
    ├─ Check if correct
    └─ Calculate P&L
    ↓
[Aggregate Results]
    ↓
Win Rate: 56.3%
Return: ₹110
```

---

## ✅ Conclusion

Your backtesting is **working correctly**! It's using:
- Real historical price data
- Real technical indicators
- Fair testing methodology (no look-ahead bias)

The 56.3% win rate is based on **actual Nifty price movements** from the past 7 days, tested with your AI prediction model.

**Next step**: Run the automated optimization to find the best parameters! 🚀

---

**Last Updated**: February 28, 2026
