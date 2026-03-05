# Month 1 Configuration - LOCKED

## Status: Data Collection Phase (Weeks 1-4)

This document defines the LOCKED configuration for Month 1. No changes should be made to these parameters until 300+ predictions are collected and analyzed.

---

## Risk Management (ACTIVE)

### Stop Loss & Take Profit
```python
STOP_LOSS_PERCENT = 0.5      # 0.5% stop loss (FIXED)
TAKE_PROFIT_PERCENT = 0.75   # 0.75% take profit (FIXED)
RISK_REWARD_RATIO = 1.5      # 1.5:1 risk:reward
```

**Rationale:**
- Simple and consistent
- Works in all market conditions
- Provides baseline performance data
- No optimization until we have data

---

## Entry Rules (CONFIGURED)

### Maximum Slippage
```python
MAX_SLIPPAGE_PERCENT = 0.1   # Max 0.1% price movement from signal
ENTRY_ORDER_TYPE = "MARKET"  # Use market orders
```

**Behavior:**
- Signal at 25000, current at 25010 (0.04%) → ENTER ✅
- Signal at 25000, current at 25030 (0.12%) → SKIP ❌

**Module:** `trade_entry_validator.py` (ready but not integrated)

---

## ATR Caps (CONFIGURED, NOT ACTIVE)

### Safety Limits
```python
ATR_MIN_PERCENT = 0.3        # Minimum stop loss (prevents too-tight stops)
ATR_MAX_PERCENT = 1.5        # Maximum stop loss (prevents wild stops)
```

**Status:** Configured but NOT in use
**Activation:** Month 2 (after 300+ samples)
**Module:** `atr_risk_manager.py` (ready for future use)

**ATR Defaults for Month 2:**
- Stop Loss: 1.0x ATR (capped between 0.3% and 1.5%)
- Target 1: 1.0x ATR
- Target 2: 1.5x ATR
- Dynamic adjustment: Month 2+ feature

---

## Time Filters (ACTIVE)

### Trading Blackouts
```python
DISABLE_OPENING_TRADES = True   # Disable 9:15-9:45 (opening volatility)
DISABLE_CLOSING_TRADES = True   # Disable 3:00-3:30 (closing volatility)
```

**Rationale:**
- Avoid high-volatility periods
- Better entry prices
- Reduces false signals

---

## Confidence Thresholds (ACTIVE)

### Minimum Confidence
```python
MIN_CONFIDENCE_TO_TRADE = 60    # Minimum 60% confidence to enter
```

**Behavior:**
- 70% confidence → Trade ✅
- 55% confidence → Skip ❌

---

## Position Sizing (ACTIVE)

### Maximum Position
```python
MAX_POSITION_SIZE = 0.1         # Max 10% of capital per trade
```

**Calculation:**
```
Position Size = Capital × (Confidence / 100) × MAX_POSITION_SIZE

Example:
- Capital: ₹100,000
- Confidence: 70%
- Position: ₹100,000 × 0.70 × 0.10 = ₹7,000
```

---

## Data Source Filtering (ACTIVE)

### Logging Rules
```python
# Only log predictions from real-time sources
- NSE API → LOG ✅
- Angel One → LOG ✅
- yfinance → SKIP ❌ (delayed data)
```

**CSV Structure:**
- File: `prediction_log.csv`
- Columns: 19 (includes data_source)
- Accumulation: Single file, grows daily
- Target: 300+ predictions for XGBoost training

---

## What's NOT Active (Month 2+)

### 1. ATR-Based Stops
- **Status:** Configured, not active
- **Activation:** After 300+ samples
- **Decision:** Keep defaults (1x, 1.5x) initially

### 2. Entry Validation Integration
- **Status:** Module ready, not integrated
- **Integration:** Backtesting first, then live
- **Timeline:** Month 2

### 3. Dynamic Optimization
- **Status:** Planned for Month 2
- **Requirements:** 300+ samples, XGBoost trained
- **Features:** Dynamic ATR multipliers, adaptive targets

---

## Month 1 Goals

### Primary Objectives
1. ✅ Keep dashboard running reliably
2. ⏳ Collect 300+ predictions with outcomes
3. ✅ Log data accurately (real-time sources only)
4. ✅ Maintain consistent risk management (0.5%/0.75%)
5. ⏳ Reach data threshold for XGBoost training

### Success Metrics
- **Predictions Logged:** 300+ (target)
- **Data Quality:** Real-time sources only
- **System Uptime:** >95%
- **CSV Integrity:** Single file, no corruption
- **Consistency:** Same parameters throughout Month 1

---

## Configuration Lock

### DO NOT CHANGE in Month 1:
- ❌ Stop loss percentage (0.5%)
- ❌ Take profit percentage (0.75%)
- ❌ Max slippage (0.1%)
- ❌ Confidence threshold (60%)
- ❌ Position sizing (10% max)
- ❌ Time filters (opening/closing blackouts)

### CAN CHANGE if needed:
- ✅ Bug fixes
- ✅ Data source improvements
- ✅ Dashboard UI enhancements
- ✅ Logging improvements
- ✅ Documentation updates

---

## Month 2 Transition Plan

### When to Transition:
- ✅ 300+ predictions collected
- ✅ XGBoost model trained
- ✅ Performance analysis complete
- ✅ Baseline metrics established

### What Changes:
1. **Week 5:** Analyze Month 1 performance
2. **Week 6:** Test ATR-based stops (1x, 1.5x defaults)
3. **Week 7:** Implement winning enhancements
4. **Week 8+:** Dynamic optimization (if data supports)

---

## Quick Reference

### Current Active System:
```
Risk Management:
  Stop Loss: 0.5% (fixed)
  Take Profit: 0.75% (fixed)
  Risk:Reward: 1.5:1

Entry Rules:
  Max Slippage: 0.1%
  Order Type: MARKET
  Validation: Not integrated yet

Time Filters:
  Opening: 9:15-9:45 (disabled)
  Closing: 3:00-3:30 (disabled)

Confidence:
  Minimum: 60%
  
Position Sizing:
  Maximum: 10% per trade
  
Data Logging:
  Sources: NSE API, Angel One only
  File: prediction_log.csv (single file)
  Target: 300+ samples
```

---

## User Decision Log

**Date:** March 2, 2026

**Decision:** "Agreed. Keep ATR defaults (1x and 1.5x) until XGBoost has 300+ samples. Dynamic adjustment is a Month 2 feature."

**Impact:**
- Month 1: Fixed 0.5%/0.75% risk management
- Month 2: Test ATR-based stops with 1x and 1.5x defaults
- Month 2+: Dynamic adjustment based on XGBoost predictions

---

## Files Reference

### Active Modules:
- `config.py` - All configuration parameters
- `prediction_logger.py` - Data logging (real-time sources only)
- `app.py` - Dashboard with visual indicators
- `data_fetcher.py` - Multi-source data pipeline

### Ready for Month 2:
- `trade_entry_validator.py` - Entry validation (0.1% slippage)
- `atr_risk_manager.py` - ATR-based risk management
- `backtesting_engine_v2.py` - Enhanced backtesting

### Documentation:
- `FUTURE_ENHANCEMENTS.md` - Month 2+ roadmap
- `ENTRY_RULES_CONFIGURED.md` - Entry validation details
- `ATR_CAPS_IMPLEMENTED.md` - ATR caps documentation
- `MONTH1_CONFIGURATION.md` - This document

---

## Summary

**Month 1 = Data Collection**
- Fixed parameters
- No optimization
- Focus on consistency
- Collect 300+ samples

**Month 2 = Analysis & Enhancement**
- Analyze performance
- Test ATR-based stops (1x, 1.5x)
- Integrate entry validation
- Optimize based on data

**Month 2+ = Dynamic Optimization**
- XGBoost-driven adjustments
- Adaptive parameters
- Continuous improvement

---

**Last Updated:** March 2, 2026

**Status:** LOCKED for Month 1 (Weeks 1-4)

**Next Review:** After 300+ predictions collected
