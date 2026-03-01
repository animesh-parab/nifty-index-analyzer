# 📈 Nifty AI Predictor

Real-time Nifty 50 prediction dashboard with AI-powered analysis, technical indicators, and options data.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Angel One API (Required)
```bash
python angel_one_setup.py
```
Follow the prompts to enter your Angel One credentials.

### 3. Download Options Instruments (Required for OI data)
```bash
python download_instruments.py
```
This downloads the Angel One instrument file for options token lookup.

### 4. Run Dashboard
```bash
streamlit run app.py
```

Or use the batch file:
```bash
START_DASHBOARD.bat
```

## 📊 Features

### Real-Time Data
- **Nifty 50 Price**: Live price from NSE/Angel One (0 delay)
- **India VIX**: Volatility index from yfinance
- **Options Data**: PCR, Max Pain, Open Interest (NSE → Angel One fallback)
- **News Sentiment**: Scheduled fetching (9 AM, 12 PM, 3 PM)

### 🔔 Price Alerts (NEW!)
- **Browser Notifications**: Get instant popups when price reaches your targets
- **Above/Below Alerts**: Set alerts for price going above or below targets
- **Custom Notes**: Add reminders for each alert
- **Alert History**: See recently triggered alerts
- **Zero Cost**: No SMS/email fees - completely free!

See [PRICE_ALERTS_GUIDE.md](PRICE_ALERTS_GUIDE.md) for detailed instructions.

### 📊 API Rate Limit Monitoring (NEW!)
- **Real-time Tracking**: Monitor all API usage as it happens
- **Smart Alerts**: Get notified before hitting limits (80% and 95% thresholds)
- **Usage Statistics**: See hourly and daily usage for each API
- **Usage Projection**: Estimate end-of-day usage during market hours
- **Token Tracking**: Track AI API token consumption
- **Zero Cost**: No additional API calls or fees

See [API_MONITORING_GUIDE.md](API_MONITORING_GUIDE.md) for detailed instructions.

### Technical Analysis
- 8 Technical Indicators (RSI, MACD, Bollinger Bands, EMA, SMA, ATR, ADX, Stochastic)
- Candlestick Pattern Detection
- Support/Resistance Levels
- Greeks Calculation (Delta, Theta, Vega)

### AI Predictions
- Dual-AI Consensus (Groq Llama 3.3 70B + Gemini 2.5 Flash)
- Rule-based prediction fallback
- Next candle prediction (5/15/30 min timeframes)
- Confidence scoring
- Price targets

### Data Sources
- **Primary**: NSE API (real-time, free)
- **Backup**: Angel One SmartAPI (real-time, free)
- **Fallback**: yfinance (15-min delay)

## 📁 Project Structure

```
nifty_ai_predictor/
├── app.py                          # Main dashboard
├── data_fetcher.py                 # Multi-source data fetching
├── angel_one_fetcher.py            # Angel One API integration
├── angel_one_setup.py              # Angel One authentication setup
├── download_instruments.py         # Download options instruments
├── indicators.py                   # Technical indicators
├── greeks.py                       # Options Greeks calculation
├── ai_engine.py                    # Rule-based predictions
├── news_fetcher_scheduled.py       # Scheduled news fetching
├── config.py                       # Configuration
├── .env                            # API credentials (create from env.example)
├── requirements.txt                # Python dependencies
├── instruments_nifty_options.csv   # Options instruments (auto-generated)
├── token_map.json                  # Token lookup map (auto-generated)
└── test_tokens_only.py             # Test options implementation
```

## 🔑 API Setup

### Angel One SmartAPI (Required)
1. Create account at https://smartapi.angelbroking.com/
2. Create 3 API apps (Trading, Market Feed, Historical)
3. Run `python angel_one_setup.py`
4. Enter credentials when prompted

### NewsAPI (Optional)
1. Get free API key from https://newsapi.org/
2. Add to `.env`: `NEWS_API_KEY=your_key_here`
3. Limited to 100 requests/day (scheduled fetching optimized)

## 📖 Documentation

### Main Documentation
- **ANGEL_ONE_INTEGRATION.md** - Angel One setup guide
- **ANGEL_ONE_OPTIONS_STATUS.md** - Options implementation status
- **ANGEL_ONE_OPTIONS_IMPLEMENTATION.md** - Technical implementation details
- **ANGEL_ONE_OPTIONS_COMPLETE.md** - Complete options documentation
- **IMPLEMENTATION_SUMMARY.md** - Quick implementation overview
- **OPTIONS_CHAIN_STRATEGY.md** - Options chain strategy
- **ANGEL_ONE_RATE_LIMITS.md** - Rate limit information

## 🧪 Testing

### Test Options Implementation
```bash
python test_tokens_only.py
```

Expected output (during market hours):
```
[SUCCESS] Token lookup working!
[SUCCESS] Options chain fetched!
PCR: 1.234
Max Pain: 25,300
```

### Test All Features
```bash
# Windows
test_all.bat

# Linux/Mac
./test_all.sh
```

## ⚙️ Configuration

Edit `config.py` to customize:
- Refresh intervals
- VIX thresholds
- PCR thresholds
- Confidence thresholds
- Candle periods

## 🔄 Data Flow

```
Dashboard (60s refresh)
    ↓
NSE API (primary) → Real-time price, VIX
    ↓ (if blocked)
Angel One API (backup) → Real-time price, candles, options
    ↓ (if failed)
yfinance (fallback) → 15-min delayed data
```

## 📊 Options Data

### NSE API (Primary)
- Fast (1-2 seconds)
- Full options chain
- Often blocked by anti-bot measures

### Angel One API (Fallback)
- Reliable (8-10 seconds first fetch)
- 21 strikes (ATM ±10)
- Cached for 5 minutes
- Requires instrument file download

## 🕐 Market Hours

- **Market Open**: 9:15 AM - 3:30 PM IST
- **Pre-Open**: 9:00 AM - 9:15 AM IST
- **Options Data**: Only available during market hours
- **News Fetching**: 9:00 AM, 12:00 PM, 3:00 PM

## 🐛 Troubleshooting

### "Token map file not found"
```bash
python download_instruments.py
```

### "Options data unavailable"
- Check if market is open (9:15 AM - 3:30 PM IST)
- Verify it's a trading day (not weekend/holiday)
- Re-download instruments if needed

### "Angel One authentication failed"
```bash
python angel_one_setup.py
```
Re-enter credentials.

### "News API rate limit"
- Scheduled fetching limits to 3 calls/day
- Check `.news_cache.json` for cached data
- Verify fetch times (9 AM, 12 PM, 3 PM)

## 📝 Environment Variables

Create `.env` file (copy from `env.example`):

```env
# Angel One API (Required)
ANGEL_API_KEY=your_api_key
ANGEL_CLIENT_ID=your_client_id
ANGEL_MPIN=your_mpin
ANGEL_TOTP_SECRET=your_totp_secret

# NewsAPI (Optional)
NEWS_API_KEY=your_news_api_key

# Groq API (Optional - for AI predictions)
GROQ_API_KEY=your_groq_api_key
```

## 🎯 Features Status

| Feature | Status | Data Source |
|---------|--------|-------------|
| Nifty Price | ✅ Working | NSE → Angel One → yfinance |
| India VIX | ✅ Working | yfinance → NSE |
| Candles | ✅ Working | Angel One → yfinance |
| Technical Indicators | ✅ Working | Calculated from candles |
| Candlestick Patterns | ✅ Working | Pattern detection |
| Options Data (PCR, Max Pain, OI) | ✅ Working | NSE → Angel One |
| News Sentiment | ✅ Working | NewsAPI (scheduled) |
| AI Predictions | ✅ Working | Rule-based engine |
| Greeks | ✅ Working | Black-Scholes model |

## 🔐 Security

- Never commit `.env` file
- Keep API keys secure
- Use environment variables for credentials
- Angel One TOTP provides additional security

## 📄 License

This project is for educational purposes only. Not financial advice.

## 🤝 Contributing

This is a personal project. Feel free to fork and modify for your own use.

## ⚠️ Disclaimer

This tool is for educational and informational purposes only. It does not constitute financial advice. Trading in financial markets involves risk. Always do your own research and consult with a qualified financial advisor before making investment decisions.

## 📞 Support

For issues or questions:
1. Check documentation files in the project
2. Review troubleshooting section above
3. Test with `test_tokens_only.py` during market hours

---

**Built with**: Python, Streamlit, Angel One SmartAPI, NSE API, yfinance

**Last Updated**: February 27, 2026
