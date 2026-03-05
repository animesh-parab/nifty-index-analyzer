# Entry Rules Configured ✅

## Status: READY FOR IMPLEMENTATION

Entry validation rules have been configured to prevent chasing trades and ensure good entry prices.

---

## Entry Rules

### Rule 1: Market Orders
- **Order Type:** MARKET
- **Execution:** Immediate
- **No waiting:** Enter on signal confirmation
- **No pullbacks:** Don't wait for price to come back

### Rule 2: Maximum Slippage
- **Max Slippage:** 0.1%
- **Tolerance:** ±25 points at Nifty 25000
- **Action if exceeded:** SKIP the trade (don't chase)

### Rule 3: Price Validation
- **Check:** Current price vs signal price
- **Within 0.1%:** Enter trade ✅
- **Beyond 0.1%:** Skip trade ❌

---

## Configuration (config.py)

```python
# Entry rules
MAX_SLIPPAGE_PERCENT = 0.1    # Max 0.1% price movement from signal
ENTRY_ORDER_TYPE = "MARKET"   # Use market orders for immediate execution
```

---

## How It Works

### Scenario 1: Good Entry ✅
```
Signal Generated: 25000
Current Price: 25010 (0.04% slippage)
Action: ENTER ✅
Entry Price: 25010
Order Type: MARKET
```

### Scenario 2: Price Moved Too Much ❌
```
Signal Generated: 25000
Current Price: 25030 (0.12% slippage)
Action: SKIP ❌
Reason: Don't chase (>0.1% movement)
```

### Scenario 3: Perfect Entry ✅
```
Signal Generated: 25000
Current Price: 25000 (0% slippage)
Action: ENTER ✅
Entry Price: 25000
Order Type: MARKET
```

---

## Acceptable Entry Range

For any signal price, calculate acceptable range:

**Formula:**
```
Tolerance = Signal Price × 0.1%
Min Price = Signal Price - Tolerance
Max Price = Signal Price + Tolerance
```

**Examples:**

| Signal Price | Min Price | Max Price | Tolerance |
|--------------|-----------|-----------|-----------|
| 25000 | 24975 | 25025 | ±25 points |
| 24000 | 23976 | 24024 | ±24 points |
| 26000 | 25974 | 26026 | ±26 points |

---

## Implementation Module

**File:** `trade_entry_validator.py`

**Key Functions:**

### 1. validate_entry_price()
```python
from trade_entry_validator import validate_entry_price

result = validate_entry_price(
    signal_price=25000,
    current_price=25010
)

print(result['valid'])  # True
print(result['slippage_percent'])  # 0.04
print(result['action'])  # "ENTER"
```

### 2. should_enter_trade()
```python
from trade_entry_validator import should_enter_trade

decision = should_enter_trade(
    signal_price=25000,
    current_price=25010,
    direction="BULLISH",
    confidence=70
)

print(decision['enter'])  # True
print(decision['entry_price'])  # 25010
print(decision['order_type'])  # "MARKET"
```

### 3. calculate_acceptable_entry_range()
```python
from trade_entry_validator import calculate_acceptable_entry_range

range_info = calculate_acceptable_entry_range(25000)

print(range_info['min_price'])  # 24975
print(range_info['max_price'])  # 25025
```

---

## Real-World Examples

### Example 1: Fast Market (Skip)
```
Time: 9:20 AM (opening volatility)
Signal: BULLISH at 25000
Current: 25040 (0.16% slippage)
Decision: SKIP ❌
Reason: Price moved too fast, don't chase
```

### Example 2: Slow Market (Enter)
```
Time: 11:00 AM (normal trading)
Signal: BULLISH at 25000
Current: 25002 (0.008% slippage)
Decision: ENTER ✅
Entry: 25010 (market order fills at 25010)
```

### Example 3: Volatile Day (Skip)
```
Time: 2:00 PM (budget announcement)
Signal: BULLISH at 25000
Current: 25050 (0.2% slippage)
Decision: SKIP ❌
Reason: Too much slippage, market too volatile
```

---

## Benefits

### 1. Prevents Chasing
- Don't enter after price has run away
- Avoid FOMO (Fear Of Missing Out)
- Better entry prices = better results

### 2. Protects Against Slippage
- Max 0.1% slippage = ₹25 per lot at 25000
- Predictable entry costs
- No surprise losses from bad fills

### 3. Simple and Fast
- No complex entry logic
- No waiting for pullbacks
- Immediate execution with market orders

### 4. Measurable
- Track slippage statistics
- Monitor skip rate
- Optimize tolerance if needed

---

## Entry Statistics Tracking

The module can track entry quality:

```python
from trade_entry_validator import get_entry_statistics

trades = [
    {'signal_price': 25000, 'entry_price': 25005},
    {'signal_price': 25100, 'entry_price': 25110},
    {'signal_price': 25200, 'entry_price': None},  # Skipped
]

stats = get_entry_statistics(trades)

print(f"Total Signals: {stats['total_trades']}")
print(f"Entered: {stats['entered_trades']}")
print(f"Skipped: {stats['trades_skipped']}")
print(f"Skip Rate: {stats['skip_rate']}%")
print(f"Avg Slippage: {stats['avg_slippage_percent']}%")
```

**Expected Results:**
- Skip Rate: 20-40% (normal)
- Avg Slippage: 0.02-0.05% (good)
- Max Slippage: <0.1% (by design)

---

## Integration with Current System

### Current Flow:
```
1. Generate prediction
2. Check confidence (>60%)
3. Check time filters (not 9:15-9:45, 3:00-3:30)
4. Enter trade immediately
```

### Enhanced Flow (Future):
```
1. Generate prediction
2. Check confidence (>60%)
3. Check time filters (not 9:15-9:45, 3:00-3:30)
4. Validate entry price (<0.1% slippage)  ← NEW
5. Enter trade if valid, skip if not      ← NEW
```

---

## Configuration Options

### Adjustable Parameters:

```python
# In config.py
MAX_SLIPPAGE_PERCENT = 0.1  # Can adjust based on experience
ENTRY_ORDER_TYPE = "MARKET"  # Or "LIMIT" for more control
```

### Recommended Ranges:
- **Max Slippage:** 0.05% - 0.2%
  - 0.05%: Very strict (more skips)
  - 0.1%: Balanced (recommended)
  - 0.2%: Lenient (fewer skips)

### Trade-offs:
- **Tighter (0.05%):**
  - Better entry prices
  - More trades skipped
  - Lower win rate (fewer opportunities)

- **Looser (0.2%):**
  - More trades entered
  - Worse entry prices
  - Higher slippage costs

**Recommendation:** Start with 0.1%, adjust based on data

---

## Test Results

### Test 1: Good Entry ✅
```
Signal: 25000
Current: 25010 (0.04% slippage)
Result: ENTER
Slippage: 0.04% (within 0.1% limit)
```

### Test 2: Price Moved Too Much ❌
```
Signal: 25000
Current: 25030 (0.12% slippage)
Result: SKIP
Reason: Don't chase (>0.1%)
```

### Test 3: Low Confidence ❌
```
Signal: 25000
Current: 25005 (0.02% slippage)
Confidence: 55%
Result: SKIP
Reason: Confidence < 60%
```

### Test 4: Perfect Entry ✅
```
Signal: 25000
Current: 25000 (0% slippage)
Result: ENTER
Slippage: 0%
```

---

## Why These Rules?

### 1. Market Orders
- **Pro:** Immediate execution, no waiting
- **Pro:** Simple and reliable
- **Con:** Slight slippage (controlled by 0.1% rule)
- **Verdict:** Best for fast-moving markets

### 2. No Pullback Waiting
- **Pro:** Don't miss trades
- **Pro:** Faster execution
- **Con:** Might enter at suboptimal price
- **Verdict:** 0.1% rule provides enough protection

### 3. 0.1% Maximum Slippage
- **Pro:** Prevents chasing
- **Pro:** Predictable costs
- **Pro:** Better entry prices
- **Verdict:** Sweet spot between strict and lenient

---

## When to Adjust

### Increase to 0.15% if:
- Skip rate >50%
- Missing too many good trades
- Market is consistently fast

### Decrease to 0.05% if:
- Slippage costs are high
- Entry prices are poor
- Win rate is low

### Monitor:
- Skip rate (target: 20-40%)
- Average slippage (target: <0.05%)
- Win rate (should improve with better entries)

---

## Future Enhancements

### Phase 1: Basic Implementation (Now)
- ✅ Configure max slippage (0.1%)
- ✅ Create validation module
- ✅ Test entry logic

### Phase 2: Integration (Week 5+)
- Add to backtesting engine
- Test on historical data
- Compare with/without validation

### Phase 3: Optimization (Week 7+)
- Analyze skip rate
- Optimize slippage tolerance
- A/B test different values

---

## Documentation

**Files:**
- `config.py` - Entry rule configuration
- `trade_entry_validator.py` - Implementation module
- `ENTRY_RULES_CONFIGURED.md` - This document
- `backtesting_engine_v2.py` - Will integrate validation

---

## Summary

✅ **Entry rules configured:**
- Max slippage: 0.1%
- Order type: MARKET
- No pullback waiting
- Don't chase trades

✅ **Module ready:** `trade_entry_validator.py`

✅ **Tested:** All scenarios working correctly

✅ **Benefits:**
- Better entry prices
- Prevents chasing
- Predictable costs
- Simple and fast

✅ **Next step:** Integrate into backtesting, test on historical data

---

**Date Added:** March 2, 2026

**Status:** Ready for implementation

**Decision Point:** Week 5+ (after XGBoost training and performance analysis)
