# 📊 Nifty AI Predictor - Model Explanation (One Page)

## 🎯 What It Does
Predicts Nifty 50 / Bank Nifty direction (BULLISH/BEARISH/SIDEWAYS) for next 5-60 minutes using AI + Technical Analysis

---

## 🔄 How It Works (Simple Flow)

```
LIVE DATA → INDICATORS → DUAL AI → PREDICTION → YOU TRADE
```

### Step 1: Collect Live Data (Every 60 seconds)
```
📊 Price Data          🔢 Options Data         📰 News              🌍 Global Markets
├─ Nifty: 25,030      ├─ PCR: 1.15           ├─ Sentiment: +0.3   ├─ Dow: +0.5%
├─ Open: 25,000       ├─ Max Pain: 25,000    ├─ Headlines: 5      ├─ Nasdaq: +0.8%
├─ High: 25,050       ├─ Call OI: 1.2M       └─ Score: Bullish    ├─ S&P: +0.6%
├─ Low: 24,990        └─ Put OI: 1.0M                             └─ VIX: 15.2
└─ Volume: 1.2M
```

### Step 2: Calculate Technical Indicators
```
RSI (14)        MACD (12,26,9)    EMA (9,21,50)     Bollinger Bands    ATR (14)
   ↓                 ↓                 ↓                   ↓              ↓
  58.2            +12.5           Uptrend          Upper: 25,100      High Vol
(Bullish)       (Bullish)        (Bullish)        (Near top)         (Caution)
```

### Step 3: Dual-AI Consensus
```
┌─────────────────────────────────────────────────────────────┐
│  GROQ AI (Llama 3.3 70B)          GEMINI AI (2.5 Flash)    │
│  ↓                                 ↓                        │
│  Analyzes all data                Analyzes all data         │
│  ↓                                 ↓                        │
│  BULLISH (70%)                    BULLISH (65%)             │
└─────────────────────────────────────────────────────────────┘
                         ↓
              ┌──────────────────────┐
              │  CONSENSUS ENGINE    │
              │  Both agree = STRONG │
              │  Confidence: 75%     │
              └──────────────────────┘
                         ↓
              📊 FINAL PREDICTION
              Direction: BULLISH
              Confidence: 75%
              Strength: STRONG
```

### Step 4: Generate Prediction
```
🎯 PREDICTION OUTPUT
├─ Direction: BULLISH ↗️
├─ Confidence: 75%
├─ Strength: STRONG
├─ Price Targets:
│  ├─ 5min:  25,040 - 25,060
│  ├─ 15min: 25,050 - 25,080
│  └─ 30min: 25,070 - 25,100
├─ Key Reasons:
│  1. RSI showing bullish momentum (58.2)
│  2. MACD positive crossover (+12.5)
│  3. Price above all EMAs (uptrend)
└─ Options Strategy: Buy Call options
```

---

## 🧮 Prediction Logic (Scoring System)

### Technical Indicators (60% weight)
```
RSI:     Bullish (+1)  │  MACD:    Bullish (+2)  │  EMA:     Uptrend (+2)
BB:      Upper half (+1)│  ATR:     High vol (-1) │  VWAP:    Above (+1)
                        │                         │
                        └─────────→ Score: +6 (Bullish)
```

### Options Data (20% weight)
```
PCR > 1.2:  Bullish (+1)  │  Max Pain:  Near current (0)
Call OI:    Increasing (+1)│  Put OI:    Stable (0)
                           │
                           └─────────→ Score: +2 (Bullish)
```

### News & Sentiment (10% weight)
```
News Score: +0.3 (Positive) → +1
Headlines:  Mostly bullish  → +1
                            │
                            └─────────→ Score: +2 (Bullish)
```

### Global Cues (10% weight)
```
US Markets: +0.6% (Positive) → +1
Asian Markets: +0.4% (Positive) → +1
                               │
                               └─────────→ Score: +2 (Bullish)
```

### Total Score Calculation
```
Technical:  +6 × 60% = +3.6
Options:    +2 × 20% = +0.4
News:       +2 × 10% = +0.2
Global:     +2 × 10% = +0.2
                      ─────
Total Score:          +4.4 → BULLISH (75% confidence)
```

---

## 🎯 Decision Rules

```
Score ≥ +3:  BULLISH (Confidence: 50 + score×5)
Score ≤ -3:  BEARISH (Confidence: 50 + |score|×5)
-3 < Score < +3:  SIDEWAYS (Confidence: 40)
```

### Consensus Adjustment
```
Both AI agree:      +10% confidence (STRONG)
One AI disagrees:   -5% confidence (MODERATE)
Both disagree:      -20% confidence (WEAK)
```

---

## 📊 Current Performance (Backtesting Results)

```
┌─────────────────────────────────────────────────────────┐
│  Win Rate: 56.3%  │  Profit Factor: 1.05  │  Status: ✅ │
├─────────────────────────────────────────────────────────┤
│  Bullish Accuracy: 48.0% ⚠️  (Needs improvement)        │
│  Bearish Accuracy: 61.5% ✅  (Working well)             │
├─────────────────────────────────────────────────────────┤
│  Total Trades: 465  │  Wins: 262  │  Losses: 203       │
│  Avg Win: ₹8.20     │  Avg Loss: ₹-10.04                │
│  Max Drawdown: ₹-853.58                                 │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Key Features

### 1. Volatility Forecasting (6 Methods)
```
Historical → Parkinson → Garman-Klass → ATR → GARCH → Ensemble
    ↓           ↓            ↓           ↓      ↓         ↓
  1.2%        1.3%         1.25%       1.1%   1.4%     1.25% (Final)
                                                           ↓
                                                    Regime: NORMAL
                                                    Trend: STABLE
```

### 2. Real-Time Data Sources
```
Angel One (Primary) → NSE API → yfinance (Fallback)
     ↓                  ↓            ↓
  0ms delay        Real-time    15min delay
```

### 3. Risk Management
```
Position Size = Capital × (Confidence/100) × 10%
Example: ₹100,000 × (75/100) × 10% = ₹7,500 per trade
```

---

## 💡 Why It Works

### Strengths ✅
1. **Dual-AI Validation**: Two AIs cross-check each other
2. **Multi-Factor Analysis**: Uses 9 technical indicators + options + news
3. **Real-Time Data**: Updates every 60 seconds
4. **Proven Accuracy**: 56.3% win rate (above breakeven)
5. **Bearish Predictions**: 61.5% accuracy (excellent)

### Limitations ⚠️
1. **Bullish Predictions**: 48% accuracy (needs improvement)
2. **Training Phase**: Model still being optimized
3. **Market Dependent**: Performance varies with market conditions
4. **No Guarantees**: Past performance ≠ future results

---

## 🚀 Optimization Strategy

```
Current: 56.3% → Target: 60%+ (4 weeks)
    ↓
1. Focus on bearish predictions (already 61.5%)
2. Improve bullish signal detection
3. Add stop loss/take profit logic
4. Test different timeframes
5. Optimize confidence thresholds
    ↓
Expected: 60-63% win rate
```

---

## 📈 Use Cases

### For Day Traders
```
5-15 min predictions → Quick scalping → High frequency
```

### For Swing Traders
```
30-60 min predictions → Position trading → Lower frequency
```

### For Options Traders
```
Volatility forecasting → Strategy selection → Premium optimization
```

---

## 🎓 Model Type

```
Hybrid Model = Rule-Based (80%) + AI Enhancement (20%)

Rule-Based:
├─ Technical indicators (RSI, MACD, EMA)
├─ Predefined thresholds
└─ Deterministic logic

AI Enhancement:
├─ Pattern recognition
├─ Context understanding
└─ Consensus validation
```

---

## 💰 Cost

```
100% FREE
├─ Angel One API: Free (10,000 calls/day)
├─ yfinance: Free (unlimited)
├─ Groq AI: Free (14,400 calls/day)
├─ Gemini AI: Free (1,500 calls/day)
└─ Total: ₹0/month
```

---

## ⚠️ Disclaimer

```
🚨 NOT FINANCIAL ADVICE
├─ Educational project only
├─ Paper trade first
├─ Use stop losses
├─ Start with small capital
└─ Trade at your own risk
```

---

## 🎯 Quick Stats

| Metric | Value | Status |
|--------|-------|--------|
| Win Rate | 56.3% | 🟡 Training |
| Profit Factor | 1.05 | 🟡 Fair |
| Bullish Accuracy | 48.0% | 🔴 Needs Work |
| Bearish Accuracy | 61.5% | 🟢 Good |
| Data Latency | 0-15s | 🟢 Real-time |
| Update Frequency | 60s | 🟢 Fast |
| Cost | ₹0 | 🟢 Free |

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT DASHBOARD                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Price   │  │ Options  │  │   News   │  │  Global  │  │
│  │  Data    │  │  Chain   │  │Sentiment │  │   Cues   │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       └─────────────┴─────────────┴─────────────┘         │
│                         ↓                                   │
│              ┌──────────────────────┐                      │
│              │  INDICATOR ENGINE    │                      │
│              │  (RSI, MACD, EMA)    │                      │
│              └──────────┬───────────┘                      │
│                         ↓                                   │
│       ┌─────────────────────────────────────┐             │
│       │      DUAL-AI CONSENSUS ENGINE       │             │
│       │  ┌──────────┐    ┌──────────┐      │             │
│       │  │  Groq AI │    │ Gemini AI│      │             │
│       │  └────┬─────┘    └────┬─────┘      │             │
│       │       └────────┬────────┘           │             │
│       │                ↓                    │             │
│       │         [Consensus Logic]           │             │
│       └─────────────────┬───────────────────┘             │
│                         ↓                                   │
│              ┌──────────────────────┐                      │
│              │   FINAL PREDICTION   │                      │
│              │  Direction + Confidence│                    │
│              └──────────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

---

**🎉 That's the entire model in one page!**

**GitHub**: https://github.com/Shiro150/nifty-index-analyzer  
**Status**: Training Phase (56.3% → 60%+ target)  
**Cost**: 100% FREE  
**Last Updated**: February 28, 2026
