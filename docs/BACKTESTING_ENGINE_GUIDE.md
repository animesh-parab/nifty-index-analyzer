# 📊 Backtesting Engine - Complete Guide

## Overview

The Backtesting Engine allows you to test your AI prediction model against historical data to evaluate its performance. This helps you understand how well your predictions would have performed in real market conditions.

## Features

### Core Capabilities
- ✅ Historical data fetching (up to 60 days intraday)
- ✅ AI prediction testing on past data
- ✅ Win/loss rate calculation
- ✅ Profit/loss simulation
- ✅ Detailed performance metrics
- ✅ Interactive visualizations
- ✅ Trade-by-trade analysis
- ✅ Export results (JSON/CSV)

### Metrics Tracked
- Total trades and predictions
- Win rate and accuracy
- Profit/loss (absolute and percentage)
- Average win/loss amounts
- Profit factor
- Maximum drawdown
- Direction-specific accuracy (bullish/bearish)
- Confidence levels

## How to Use

### 1. Access Backtesting

**From Dashboard:**
1. Look for "📊 Backtesting Engine" in the sidebar
2. Click "🚀 Open Backtesting" button
3. Backtesting UI will appear below the main dashboard

### 2. Configure Backtest

**Parameters:**

1. **Index** - Choose NIFTY 50 or BANK NIFTY
2. **Days** - Number of days to backtest (1-60)
   - More days = more data, longer processing time
   - Recommended: 7-14 days for quick tests
3. **Interval** - Candle timeframe
   - 5m: Most granular, more trades
   - 15m: Balanced
   - 30m/1h: Fewer trades, longer timeframes
4. **Prediction Timeframe** - How far ahead to predict (5-120 minutes)
   - Should match your trading style
   - Shorter = more trades, less accuracy
   - Longer = fewer trades, potentially more accurate
5. **Initial Capital** - Starting amount for simulation (₹10,000 - ₹10,000,000)

### 3. Run Backtest

1. Set your parameters
2. Click "🚀 Run Backtest"
3. Wait for processing (may take 1-5 minutes depending on data size)
4. View results automatically displayed

### 4. Analyze Results

**Performance Summary:**
- Total Return: Absolute profit/loss
- Win Rate: Percentage of correct predictions
- Final Capital: Ending balance
- Profit Factor: Ratio of wins to losses

**Detailed Metrics:**
- Trade statistics (wins, losses, averages)
- Direction accuracy (bullish vs bearish)
- Risk metrics (drawdown, profit factor)

**Visualizations:**
- Equity curve: Capital over time
- Win/loss distribution: Bar chart
- Direction accuracy: Comparison chart

**Trade History:**
- Last 20 trades displayed
- Full details: entry, exit, P&L, accuracy
- Timestamp and confidence levels

### 5. Export Results

**JSON Report:**
- Complete backtest data
- All metrics and trades
- Saved to `backtest_report.json`

**CSV Trades:**
- Trade-by-trade details
- Easy to analyze in Excel
- Saved to `backtest_trades.csv`

## Understanding Results

### Win Rate
- **>60%**: Excellent - Model is highly accurate
- **50-60%**: Good - Model has edge
- **40-50%**: Fair - Needs improvement
- **<40%**: Poor - Model needs major revision

### Profit Factor
- **>2.0**: Excellent - Strong profitability
- **1.5-2.0**: Good - Profitable system
- **1.0-1.5**: Fair - Marginally profitable
- **<1.0**: Poor - Losing system

### Return on Capital
- **>10%**: Excellent for short period
- **5-10%**: Good performance
- **0-5%**: Modest gains
- **<0%**: Losses - review strategy

### Max Drawdown
- Lower is better
- Should be <20% of capital
- Indicates risk management quality

## Best Practices

### 1. Start Small
- Begin with 7 days, 5m interval
- Understand results before scaling up
- Test different timeframes

### 2. Compare Timeframes
- Run multiple backtests with different intervals
- Compare 5m vs 15m vs 30m
- Find optimal timeframe for your strategy

### 3. Test Both Indices
- Backtest NIFTY and BANK NIFTY separately
- Different indices may have different accuracy
- Choose best performing index

### 4. Analyze Patterns
- Look at direction accuracy
- Bullish vs bearish performance
- Time of day patterns (if visible in data)

### 5. Realistic Expectations
- Past performance ≠ future results
- Use as guidance, not guarantee
- Consider market conditions

## Limitations

### Data Limitations
- Maximum 60 days for intraday data (yfinance limit)
- Historical data may have gaps
- No tick-by-tick data

### Simulation Limitations
- No slippage modeling
- No transaction costs
- Perfect execution assumed
- No market impact

### Model Limitations
- Simplified options data (PCR, max pain)
- No real-time news sentiment
- Rule-based predictions only (not full AI)
- No Greeks calculation in backtest

## Technical Details

### How It Works

1. **Data Fetching**
   - Downloads historical OHLCV data
   - Calculates technical indicators
   - Filters to market hours

2. **Prediction Generation**
   - For each candle, generates prediction
   - Uses only data available at that time (no lookahead)
   - Applies same logic as live predictions

3. **Evaluation**
   - Compares prediction to actual outcome
   - Calculates accuracy and P&L
   - Tracks capital changes

4. **Metrics Calculation**
   - Aggregates all trades
   - Computes win rate, profit factor, etc.
   - Generates visualizations

### Position Sizing
- Based on prediction confidence
- Higher confidence = larger position
- Maximum 10% of capital per trade
- Formula: `position_size = capital * (confidence / 100) * 0.1`

### Trade Logic
- **Bullish**: Long position (buy)
- **Bearish**: Short position (sell)
- **Sideways**: No trade (skip)

## Examples

### Example 1: Quick Test
```
Index: NIFTY 50
Days: 7
Interval: 5m
Timeframe: 30 min
Capital: ₹100,000

Expected:
- ~200-300 predictions
- Processing time: 2-3 minutes
- Good for initial testing
```

### Example 2: Comprehensive Test
```
Index: NIFTY 50
Days: 30
Interval: 15m
Timeframe: 60 min
Capital: ₹500,000

Expected:
- ~400-600 predictions
- Processing time: 5-10 minutes
- Better statistical significance
```

### Example 3: Bank Nifty Test
```
Index: BANK NIFTY
Days: 14
Interval: 5m
Timeframe: 30 min
Capital: ₹200,000

Expected:
- ~300-400 predictions
- Processing time: 3-5 minutes
- Compare with Nifty results
```

## Troubleshooting

### Issue: No data fetched
**Solution:**
- Check internet connection
- Try fewer days
- Use different interval
- yfinance may be temporarily down

### Issue: Processing takes too long
**Solution:**
- Reduce number of days
- Use larger interval (15m instead of 5m)
- Close other applications
- Be patient (large datasets take time)

### Issue: Low win rate
**Solution:**
- This is feedback, not an error
- Review prediction logic
- Try different timeframes
- Consider market conditions during test period

### Issue: Negative returns
**Solution:**
- Normal for some periods
- Test different date ranges
- Adjust position sizing
- Review risk management

## Command Line Usage

You can also run backtests from command line:

```bash
# Quick test
python backtesting_engine.py

# Custom test
python -c "from backtesting_engine import quick_backtest; quick_backtest(days=14, interval='15m', timeframe=60)"
```

## API Reference

### BacktestingEngine Class

```python
from backtesting_engine import BacktestingEngine

# Initialize
engine = BacktestingEngine(
    symbol="^NSEI",  # or "^NSEBANK"
    initial_capital=100000
)

# Run backtest
results = engine.run_backtest(
    days=7,
    interval="5m",
    timeframe_minutes=30
)

# Generate report
engine.generate_report("my_backtest.json")
```

### Results Structure

```python
{
    'metrics': {
        'total_trades': int,
        'winning_trades': int,
        'losing_trades': int,
        'win_rate': float,
        'total_pnl': float,
        'avg_win': float,
        'avg_loss': float,
        'profit_factor': float,
        'max_drawdown': float,
        'bullish_accuracy': float,
        'bearish_accuracy': float
    },
    'summary': {
        'total_predictions': int,
        'correct_predictions': int,
        'win_rate': float,
        'initial_capital': float,
        'final_capital': float,
        'total_return': float,
        'return_pct': float
    },
    'trades': [
        {
            'timestamp': datetime,
            'predicted_direction': str,
            'actual_direction': str,
            'entry_price': float,
            'exit_price': float,
            'pnl': float,
            'pnl_pct': float,
            'confidence': float,
            'correct': bool
        },
        ...
    ]
}
```

## Performance Tips

### For Faster Backtests
1. Use larger intervals (15m, 30m)
2. Reduce number of days
3. Close other applications
4. Use SSD for data storage

### For More Accurate Results
1. Use more days (20-30)
2. Use smaller intervals (5m)
3. Test multiple timeframes
4. Compare different periods

## Future Enhancements

Planned improvements:
- Walk-forward optimization
- Parameter optimization
- Monte Carlo simulation
- Transaction cost modeling
- Slippage simulation
- Multiple strategy comparison
- Real AI model backtesting (not just rule-based)
- Options strategy backtesting
- Risk-adjusted metrics (Sharpe, Sortino)

## FAQ

**Q: How accurate is the backtest?**
A: It's a simulation using simplified assumptions. Real trading will differ due to slippage, costs, and execution delays.

**Q: Can I backtest options strategies?**
A: Not yet. Currently only directional predictions. Options backtesting is planned.

**Q: Why is my win rate low?**
A: Market conditions vary. A 50-60% win rate is actually good for directional trading.

**Q: How much data should I use?**
A: Start with 7-14 days. More data = better statistics but longer processing.

**Q: Can I backtest custom strategies?**
A: Currently uses built-in prediction model. Custom strategies planned for future.

**Q: Does it account for transaction costs?**
A: No, it assumes zero costs. Subtract ~0.1-0.2% per trade for realistic results.

**Q: Can I backtest on daily data?**
A: Yes, use interval="1d" for daily candles.

**Q: How do I interpret profit factor?**
A: Profit Factor = Total Wins / Total Losses. >1.5 is good, >2.0 is excellent.

## Support

For issues or questions:
1. Check this guide first
2. Review error messages
3. Try with default parameters
4. Check logs for details

## Conclusion

The Backtesting Engine is a powerful tool for evaluating your AI prediction model. Use it to:
- Understand model performance
- Identify strengths and weaknesses
- Optimize parameters
- Build confidence in predictions
- Make data-driven decisions

Remember: Past performance doesn't guarantee future results, but it's valuable feedback for improvement!

---

**Last Updated:** February 27, 2026
**Version:** 1.0.0
