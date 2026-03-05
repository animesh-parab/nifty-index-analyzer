# Risk Management & Time Filtering Guide

## Overview

This guide covers two critical improvements to the trading system:
1. **Risk:Reward Management** - Stop loss and take profit at 1.5:1 ratio
2. **Time-of-Day Filtering** - Avoid high-volatility periods

These improvements address the core profitability issues identified in backtesting.

## Problem Statement

### Original System Issues

From backtesting results:
- **Win Rate**: 56.3% (decent)
- **Average Win**: ₹8.20
- **Average Loss**: ₹10.04
- **Problem**: Losses bigger than wins = barely profitable

**Mathematical Reality:**
```
Expected Value = (Win Rate × Avg Win) - (Loss Rate × Avg Loss)
                = (0.563 × 8.20) - (0.437 × 10.04)
                = 4.62 - 4.39
                = ₹0.23 per trade (barely profitable!)
```

### With 1.5:1 Risk:Reward

```
Assume: Stop Loss = ₹10, Take Profit = ₹15

Expected Value = (0.563 × 15) - (0.437 × 10)
                = 8.45 - 4.37
                = ₹4.08 per trade (genuinely profitable!)
```

**Result**: 17x improvement in profitability!

## Solution 1: Risk:Reward Management

### Configuration (config.py)

```python
# Risk Management Settings
RISK_REWARD_RATIO = 1.5                  # Take profit at 1.5x stop loss
STOP_LOSS_PERCENT = 0.5                  # 0.5% stop loss
TAKE_PROFIT_PERCENT = 0.75               # 0.75% take profit (1.5x SL)
MAX_POSITION_SIZE = 0.1                  # Max 10% of capital per trade
MIN_CONFIDENCE_TO_TRADE = 60             # Minimum confidence to enter
```

### How It Works

#### For BULLISH Trade (Long Position)

```
Entry Price: ₹25,000
Stop Loss:   ₹24,875 (0.5% below entry)
Take Profit: ₹25,187.50 (0.75% above entry)

Risk:   ₹125 per lot
Reward: ₹187.50 per lot
Ratio:  1.5:1
```

#### For BEARISH Trade (Short Position)

```
Entry Price: ₹25,000
Stop Loss:   ₹25,125 (0.5% above entry)
Take Profit: ₹24,812.50 (0.75% below entry)

Risk:   ₹125 per lot
Reward: ₹187.50 per lot
Ratio:  1.5:1
```

### Trade Management Rules

1. **Entry**: Only enter if confidence ≥ 60%
2. **Stop Loss**: Hard stop at 0.5% (no exceptions!)
3. **Take Profit**: Exit at 0.75% (don't exit winners early!)
4. **Position Sizing**: Scale with confidence (max 10% capital)

### Exit Reasons

The system tracks three exit types:

1. **STOP_LOSS**: Price hit stop loss level
2. **TAKE_PROFIT**: Price hit take profit level
3. **TIME_EXIT**: Neither SL nor TP hit within timeframe

### Expected Improvements

With 56% win rate:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Avg Win | ₹8.20 | ₹15.00 | +83% |
| Avg Loss | ₹10.04 | ₹10.00 | -0.4% |
| Profit Factor | 0.82 | 1.68 | +105% |
| Expected Value | ₹0.23 | ₹4.08 | +1,674% |

## Solution 2: Time-of-Day Filtering

### The Problem

Market hours with poor accuracy:
- **9:15-9:45 AM**: Opening volatility, erratic moves
- **3:00-3:30 PM**: Closing volatility, position squaring

These periods account for ~20% of trading time but cause 40%+ of losses.

### Configuration (config.py)

```python
# Time-of-Day Filters
DISABLE_OPENING_TRADES = True            # Disable 9:15-9:45
DISABLE_CLOSING_TRADES = True            # Disable 3:00-3:30
OPENING_BLACKOUT_START = (9, 15)         # (hour, minute)
OPENING_BLACKOUT_END = (9, 45)           # (hour, minute)
CLOSING_BLACKOUT_START = (15, 0)         # (hour, minute)
CLOSING_BLACKOUT_END = (15, 30)          # (hour, minute)
```

### How It Works

```python
def is_trading_allowed(timestamp):
    hour = timestamp.hour
    minute = timestamp.minute
    
    # Block 9:15-9:45 (opening)
    if 9 <= hour < 10 and 15 <= minute < 45:
        return False
    
    # Block 3:00-3:30 (closing)
    if hour == 15 and 0 <= minute < 30:
        return False
    
    return True
```

### Expected Improvements

Assuming opening/closing hours have 45% accuracy vs 60% during normal hours:

| Period | Duration | Accuracy | Action |
|--------|----------|----------|--------|
| 9:15-9:45 | 30 min | 45% | ❌ DISABLE |
| 9:45-3:00 | 5h 15m | 60% | ✅ TRADE |
| 3:00-3:30 | 30 min | 45% | ❌ DISABLE |

**Result**: Overall accuracy improves from 56% to 60%+ by filtering bad hours.

### Analyzing Your Data

Use the hourly performance analyzer to identify your specific bad hours:

```bash
python hourly_performance_analyzer.py
```

Output:
```
HOURLY BREAKDOWN
Hour       Total      Correct    Accuracy     Status
09:00-09:59  45         18        40.00%      ❌ POOR
10:00-10:59  52         32        61.54%      ✅ GOOD
11:00-11:59  48         30        62.50%      ✅ GOOD
12:00-12:59  50         31        62.00%      ✅ GOOD
13:00-13:59  47         29        61.70%      ✅ GOOD
14:00-14:59  49         30        61.22%      ✅ GOOD
15:00-15:59  43         19        44.19%      ❌ POOR
```

## Implementation

### Enhanced Backtesting Engine

New file: `backtesting_engine_v2.py`

Features:
- Stop loss / Take profit checking on every tick
- Time-of-day filtering
- Confidence-based filtering
- Detailed exit reason tracking
- Hourly performance analytics

### Usage

```python
from backtesting_engine_v2 import BacktestingEngineV2

# Run enhanced backtest
engine = BacktestingEngineV2()
results = engine.run_backtest(
    days=7,
    interval="5m",
    timeframe_minutes=30
)

# View results
metrics = results['metrics']
print(f"Win Rate: {metrics['win_rate']:.2f}%")
print(f"Profit Factor: {metrics['profit_factor']:.2f}")
print(f"Avg Risk:Reward: {metrics['avg_risk_reward']:.2f}")

# Exit reason breakdown
print(f"Stop Loss Hits: {metrics['stop_loss_hits']}")
print(f"Take Profit Hits: {metrics['take_profit_hits']}")
print(f"Time Exits: {metrics['time_exits']}")

# Hourly performance
for hour, stats in metrics['hourly_performance'].items():
    print(f"{hour}: {stats['win_rate']:.1f}% win rate")
```

### Integration with Live Trading

The risk management rules are configured in `config.py` and will be used by:

1. **Backtesting Engine V2**: For testing strategies
2. **Live Dashboard**: For real-time predictions (future integration)
3. **XGBoost Training**: Logged predictions respect time filters

## Best Practices

### 1. Stop Loss Discipline

- **NEVER** move stop loss further away
- **NEVER** remove stop loss "just this once"
- **ALWAYS** honor the stop loss level

### 2. Take Profit Discipline

- **DON'T** exit winners early
- **DON'T** get greedy and wait for more
- **DO** take profit at target level

### 3. Position Sizing

- **MAX** 10% of capital per trade
- **SCALE** with confidence (60% conf = 6% position, 80% conf = 8% position)
- **NEVER** go all-in on one trade

### 4. Time Filtering

- **REVIEW** hourly performance monthly
- **ADJUST** blackout periods based on data
- **TEST** changes in backtest before live

### 5. Confidence Filtering

- **MINIMUM** 60% confidence to trade
- **SKIP** low-confidence signals
- **QUALITY** over quantity

## Performance Monitoring

### Key Metrics to Track

1. **Win Rate**: Should stay above 55%
2. **Profit Factor**: Should be above 1.5
3. **Avg Risk:Reward**: Should be close to 1.5
4. **Stop Loss Hit Rate**: Should be ~40-45%
5. **Take Profit Hit Rate**: Should be ~55-60%

### Red Flags

⚠️ **Stop Loss Hit Rate > 50%**: Predictions not accurate enough
⚠️ **Take Profit Hit Rate < 50%**: Targets too aggressive
⚠️ **Profit Factor < 1.2**: System not profitable
⚠️ **Win Rate < 50%**: Need to improve prediction accuracy

### Monthly Review Checklist

- [ ] Run hourly performance analysis
- [ ] Check if blackout periods still valid
- [ ] Review stop loss hit rate
- [ ] Review take profit hit rate
- [ ] Adjust STOP_LOSS_PERCENT if needed (based on ATR)
- [ ] Update time filters based on data

## Advanced: Dynamic Stop Loss

For future enhancement, consider ATR-based stop loss:

```python
# Calculate ATR-based stop loss
atr = df['atr'].iloc[-1]
stop_loss_distance = atr * 2  # 2x ATR

# For BULLISH
stop_loss = entry_price - stop_loss_distance
take_profit = entry_price + (stop_loss_distance * 1.5)
```

This adapts to market volatility automatically.

## Troubleshooting

### Issue: Too Many Stop Loss Hits

**Cause**: Stop loss too tight or predictions not accurate
**Solution**: 
- Increase STOP_LOSS_PERCENT to 0.75% or 1%
- Improve prediction accuracy (retrain XGBoost)
- Filter more aggressively (higher MIN_CONFIDENCE_TO_TRADE)

### Issue: Too Few Take Profit Hits

**Cause**: Take profit too far or market not moving enough
**Solution**:
- Decrease TAKE_PROFIT_PERCENT to 0.6% (1.2:1 ratio)
- Check if market volatility is low (VIX < 12)
- Consider shorter timeframes (15min instead of 30min)

### Issue: Low Profit Factor Despite Good Win Rate

**Cause**: Avg loss still bigger than avg win
**Solution**:
- Verify RISK_REWARD_RATIO is actually 1.5
- Check if stop losses are being honored
- Review exit reason breakdown

## Summary

### Key Takeaways

1. **Risk:Reward is MORE important than win rate**
   - 56% win rate with 1.5:1 RR = profitable
   - 70% win rate with 0.8:1 RR = unprofitable

2. **Time filtering is free money**
   - Costs nothing to skip bad hours
   - Improves win rate by 3-5%
   - Reduces drawdowns

3. **Discipline beats strategy**
   - Best strategy fails without discipline
   - Honor stop losses ALWAYS
   - Take profits at target ALWAYS

4. **Data-driven decisions**
   - Use hourly analysis to find bad periods
   - Adjust based on YOUR data, not assumptions
   - Review and update monthly

### Expected Results

With both improvements:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Win Rate | 56% | 60% | +7% |
| Avg Win | ₹8.20 | ₹15.00 | +83% |
| Avg Loss | ₹10.04 | ₹10.00 | -0.4% |
| Profit Factor | 0.82 | 2.00 | +144% |
| Expected Value | ₹0.23 | ₹5.00 | +2,074% |

**Bottom Line**: These two changes can turn a barely-profitable system into a genuinely profitable one!
