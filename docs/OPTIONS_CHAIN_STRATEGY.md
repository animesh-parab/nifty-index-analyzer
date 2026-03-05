# 📊 Options Chain Integration Strategy

## Angel One Rate Limits (from official docs):

### Key Endpoints:
| Endpoint | Per Second | Per Minute | Per Hour |
|----------|-----------|------------|----------|
| `getLtpData` | 10 | 500 | 5000 |
| `getCandleData` | 3 | 180 | 5000 |
| `quote` (market data) | 10 | 500 | 5000 |

---

## Problem:

To get full options chain data (PCR, Max Pain, OI), we need:
- **21 strikes** (ATM ±10 strikes at 50-point intervals)
- **2 calls per strike** (CE + PE) = 42 API calls
- **Current refresh**: Every 60 seconds
- **Required calls**: 42 calls/minute = **EXCEEDS LIMIT** ❌

### Rate Limit Math:
- `getLtpData` limit: 10/second, 500/minute
- Our need: 42 calls/minute
- **Status**: ✅ WITHIN LIMIT (42 < 500)

But we need to be smart about it!

---

## Solution: Smart Caching Strategy

### Strategy 1: Longer Cache (RECOMMENDED)
**Refresh options data every 5 minutes instead of 60 seconds**

#### Why This Works:
- Options OI doesn't change drastically every minute
- PCR and Max Pain are strategic indicators, not scalping indicators
- Reduces API calls from 42/min to 8.4/min (42 calls / 5 minutes)
- Well within rate limits
- Still provides valuable insights

#### Implementation:
```python
@st.cache_data(ttl=300)  # 5 minutes instead of 55 seconds
def cached_options():
    return get_options_chain()
```

#### Dashboard Display:
```
PCR: 1.234
Max Pain: 25,500
Open Interest: 1.2M contracts
⏱ Updated: 5 minutes ago
```

---

### Strategy 2: Reduced Strike Range
**Fetch fewer strikes (ATM ±5 instead of ±10)**

#### Why This Works:
- Most trading happens near ATM
- Reduces calls from 42 to 22 (11 strikes × 2)
- Still captures 90% of relevant OI
- Faster refresh possible

#### Trade-offs:
- Less accurate Max Pain (missing far OTM data)
- Still good PCR calculation
- Acceptable for most use cases

---

### Strategy 3: Batch API Calls
**Use Angel One's batch quote API if available**

#### Why This Works:
- Single API call for multiple symbols
- Much faster and efficient
- Within rate limits

#### Need to Check:
- If Angel One supports batch quote for options
- If not, use Strategy 1

---

## Recommended Implementation:

### Phase 1: Basic Options Chain (5-min cache)
```python
# In angel_one_fetcher.py
def fetch_options_chain_angel(expiry_date=None):
    """
    Fetch options chain with smart caching
    - Fetches ATM ±10 strikes (21 strikes)
    - 42 API calls total (CE + PE)
    - Cached for 5 minutes
    """
    # Get current Nifty price
    nifty_data = fetch_nifty_angel()
    current_price = nifty_data['price']
    atm_strike = round(current_price / 50) * 50
    
    # Strikes to fetch (ATM ±10)
    strikes = [atm_strike + (i * 50) for i in range(-10, 11)]
    
    options_data = []
    call_oi_total = 0
    put_oi_total = 0
    
    # Fetch each strike (with rate limiting)
    for strike in strikes:
        # Fetch CE
        ce_data = fetch_option_contract(strike, 'CE', expiry_date)
        if ce_data:
            call_oi_total += ce_data.get('oi', 0)
            options_data.append(ce_data)
        
        # Fetch PE
        pe_data = fetch_option_contract(strike, 'PE', expiry_date)
        if pe_data:
            put_oi_total += pe_data.get('oi', 0)
            options_data.append(pe_data)
        
        # Rate limiting: 0.1 second delay between calls
        time.sleep(0.1)  # 10 calls/second limit
    
    # Calculate PCR
    pcr = put_oi_total / call_oi_total if call_oi_total > 0 else 0
    
    # Calculate Max Pain
    max_pain = calculate_max_pain(options_data)
    
    return {
        'pcr': pcr,
        'max_pain': max_pain,
        'call_oi': call_oi_total,
        'put_oi': put_oi_total,
        'options_data': pd.DataFrame(options_data)
    }
```

### Phase 2: Update app.py
```python
# Change cache TTL from 55 to 300 seconds
@st.cache_data(ttl=300)  # 5 minutes
def cached_oi():
    return get_options_chain()
```

### Phase 3: Add "Last Updated" timestamp
```python
# In dashboard display
st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">PCR</div>
    <div class="metric-value">{pcr:.3f}</div>
    <div style="font-size:0.6rem;color:#8b949e;">
        Updated: {time_since_update} ago
    </div>
</div>
""")
```

---

## API Call Budget:

### Current Usage (without options):
- Nifty price: 1 call/60s = 1 call/min
- VIX: 1 call/60s = 1 call/min
- Candles: 1 call/60s = 1 call/min
- **Total**: 3 calls/min

### With Options (5-min cache):
- Nifty price: 1 call/min
- VIX: 1 call/min
- Candles: 1 call/min
- Options: 42 calls/5min = 8.4 calls/min
- **Total**: 13.4 calls/min

### Rate Limit Check:
- Limit: 500 calls/min
- Usage: 13.4 calls/min
- **Headroom**: 486.6 calls/min (97% available) ✅

---

## Timeline:

### Immediate (5 minutes):
1. Update `angel_one_fetcher.py` with options chain function
2. Add rate limiting (0.1s delay between calls)
3. Update `app.py` cache TTL to 300 seconds
4. Add "Last Updated" timestamp to options metrics

### Testing (10 minutes):
1. Test during market hours
2. Verify PCR calculation
3. Verify Max Pain calculation
4. Check rate limit compliance

### Optimization (later):
1. Investigate batch API support
2. Add WebSocket for real-time OI updates
3. Optimize strike range based on volatility

---

## Expected Results:

### Before (yfinance):
- PCR: 0.000 ❌
- Max Pain: 0 ❌
- OI: Not available ❌

### After (Angel One with 5-min cache):
- PCR: 1.234 ✅ (real value)
- Max Pain: 25,500 ✅ (calculated)
- OI: 1.2M contracts ✅ (total)
- Update frequency: Every 5 minutes
- API calls: 8.4/min (well within limits)

---

## User Experience:

### Dashboard Behavior:
1. **First Load**: Fetches options data (takes ~5 seconds for 42 calls)
2. **Next 5 Minutes**: Uses cached data (instant)
3. **After 5 Minutes**: Refreshes options data
4. **Price/VIX**: Still updates every 60 seconds (real-time)

### Why 5 Minutes is OK:
- Options OI changes slowly (not tick-by-tick)
- PCR is a strategic indicator (not for scalping)
- Max Pain is calculated once per day typically
- 5-minute refresh is still very good for options analysis
- Professional platforms often use 5-10 minute refresh for options

---

## Bottom Line:

✅ **YES, we can implement options chain without hitting rate limits!**

Strategy:
- Cache options data for 5 minutes (instead of 60 seconds)
- Use 42 API calls every 5 minutes = 8.4 calls/min
- Well within 500 calls/min limit
- Still provides excellent options analysis
- Price and VIX remain real-time (60s refresh)

**Ready to implement?** 🚀
