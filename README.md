# 🚀 Enhanced Binance Crypto Dashboard (Spot)

A production-ready, high-performance crypto trading and surveillance dashboard for **BTC/USDT, ETH/USDT, SOL/USDT, and BNB/USDT** Spot markets on Binance.

![Platform](https://img.shields.io/badge/Market-Binance%20Spot-blue)
![Assets](https://img.shields.io/badge/Assets-BTC%20%7C%20ETH%20%7C%20SOL%20%7C%20BNB-brightgreen)
![Timeframe](https://img.shields.io/badge/Timeframe-1h%2F4h%2F8h%2F24h-green)
![Tech](https://img.shields.io/badge/Stack-FastAPI%20%2B%20React%20%2B%20Docker-orange)

## ✨ New Features (V1.9.0)

### 🏗️ V1.9.0: Architectural Overhaul & Stability
- **Modular Architecture**: Extracted core JSON processing and numeric sanitization to a new dedicated module: `/backend/utils.py`.
- **Confluence Breakdown UI**: Hovering over the Confidence score now reveals a detailed breakdown of active technical factors (RSI, MACD, Volume, etc.) contributing to the signal.
- **Production-Grade Logging**: Replaced `print` statements with a comprehensive `logging` configuration with formatted timestamps and severity levels.
- **Performance Optimization**: Introduced a global singleton `httpx.AsyncClient` with connection pooling, significantly reducing overhead for webhooks and API calls.
- **Security & CORS Hardening**: Restricts API access to authorized domains and methods; added a dedicated `GET /api/health` endpoint for monitoring.
- **Enhanced Type Safety**: Full type hinting (Python typing + Pydantic) and Google-style docstrings across the backend.
- **Improved Data Integrity**: Enhanced recursive JSON sanitizer in `utils.py` to handle NumPy types and prevent `NaN`/`Infinity` crashes.

## ✨ New Features (V1.8.6)

### 🌟 Expanded Asset Coverage
- **4 Major Cryptocurrencies**: Bitcoin (BTC), Ethereum (ETH), Solana (SOL), and Binance Coin (BNB)
- **Unified Monitoring**: All 4 assets receive identical technical analysis and signal generation
- **Real-time Dashboard**: 2x2 grid layout with synchronized WebSocket updates (2s refresh rate)

### 🎯 Advanced Strategy Confluences
- **🛡️ RSI Divergence Detection**: Identifies Bullish/Bearish divergences between price and RSI for high-conviction entries.
- **📊 Volume Validation**: Signals filtered by volume spikes relative to 20-period Simple Moving Average.
- **📡 H4 Trend Filtering**: Higher-timeframe filter using H4 SMA 50 to ensure signals align with broader market direction.
- **🔐 Macro Regime Filter**: BUY signals blocked in BEAR regime (SMA50 < SMA200 on H4), SELL blocked in BULL regime.
- **2-Bar Confirmation**: Previous bar must show same RSI/MACD direction before triggering signal.

### 📈 Confidence & Winrate Metrics
- **Confidence Score (0-100)**: Dynamically calculated based on 6+ confluence factors (RSI extremes, divergence, MACD, H4 alignment, volume, trend).
- **Winrate Percentage**: Historical success rate of the current signal configuration over 200-candle window.
- **Key Insight**: High Confidence ≠ Automatic BUY/SELL. Signal requires ALL strict entry criteria. HOLD with high confluence indicates market strength waiting for optimal entry.

### 🛡️ Data Integrity & Stability
- **Recursive JSON Sanitizer**: Global backend protection against `NaN` and `Infinity` values, preventing silent WebSocket crashes.
- **Auto-Reconnect Hook**: Frontend WebSocket logic automatically reconnects every 5 seconds on network drops.
- **Float64 Type Enforcement**: Ensures all numeric data is properly typed and validated.
- **Bulletproof Calculations**: Technical indicators include explicit type casting and corrupted data dropping.

### 📈 Extended Multi-Timeframe Analysis
- **Real-time Tracking**: Price changes across **1h, 4h, 8h, and 24h** intervals
- **H1 Core Analysis**: Primary signals based on 1-hour candles with 250-bar lookback
- **H4 Trend Context**: 4-hour candles inform macro regime and trend validation
- **Complete State Reporting**: Every update includes RSI state (OVERSOLD/NEUTRAL/OVERBOUGHT), MACD direction, SMA relationships, and divergence status

### 📜 Persistent Signal History
- **Dedicated UI Panel**: Tracks every signal change (HOLD → BUY → SELL) with timestamps and prices
- **Local Storage**: `signal_history.json` persists up to 100 recent transitions
- **Metadata**: Each entry logs old_signal, new_signal, price, confidence, and winrate at moment of change

### 🔔 Discord Notifications
- **Instant Alerts**: Webhook delivery on any signal change
- **Rich Embeds**: Color-coded (green=BUY, red=SELL, gray=HOLD) with price and symbol info
- **Emoji Indicators**: 🚀 (BUY), 🔻 (SELL), ⏱️ (HOLD)

### 🛠️ Robust Monitoring Loop
- **30-Second Update Cycle**: Backend queries Binance API for all 4 symbols in parallel
- **Per-Crypto Error Isolation**: One asset's downtime doesn't affect others
- **Graceful Degradation**: Missing data fields default to 0.0 with safe guards

## 🛠️ Tech Stack
- **Frontend:** React (Vite), Tailwind CSS, Lucide Icons, Fetch API.
- **Backend:** FastAPI, `python-binance` (Async), `pandas_ta`, `httpx` (for webhooks).
- **Infrastructure:** Docker & Docker Compose (Containerized).
- **Real-time:** WebSockets for instant ticker and indicator transmission.

## 📁 Project Structure
```text
crypto-dashboard/
├── backend/
│   ├── main.py        - FastAPI entrypoint & Global Lifecycle Management
│   ├── logic.py       - RSI Divergence, Strategy Confluences, Signal Generation
│   ├── utils.py       - Shared utilities: JSON safety, Numeric sanitization
│   ├── check_market_match.py - Backtest utilities
│   ├── backtest_full.py - Full strategy backtest
│   ├── signal_history.json - Persistent signal changes (100 entries)
│   ├── trade_history.json  - Persistent execution logs
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/ - TickerCard, SignalHistory, TradeHistory, TradeForm, NotificationSettings
│   │   ├── hooks/      - useBinanceSocket (WebSocket + Auto-reconnect)
│   │   ├── App.jsx     - Main dashboard grid (2x2 for 4 assets)
│   │   └── main.jsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🚀 Setup & Operation

### 1. Prerequisites
- [Docker](https://www.docker.com/) installed on your machine.
- (Optional) Binance API key/secret for manual trading.
- (Optional) Discord webhook URL for alerts.

### 2. Quick Launch
From the `crypto-dashboard/` root directory:
```bash
docker-compose up --build
```
- **Dashboard:** [http://localhost:5173](http://localhost:5173)
- **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Remote Access (Tailscale)
```bash
# Access from anywhere via Tailscale VPN
https://crypto.chantilly-shaula.ts.net
```

### 4. Usage
1. **Monitor**: View BTC, ETH, SOL, BNB price action alongside real-time signals and analysis.
2. **Analyze**: Check Confidence Score and Winrate metrics to understand signal strength.
3. **History**: Scroll to Signal History to see why signals changed, including all technical states.
4. **Alerts**: Paste your Discord Webhook URL to receive instant notifications on signal transitions.
5. **Trade**: (Optional) Input Binance API credentials for manual Spot orders.

## 🧠 Strategy Logic (V1.8 Confluence Filtering)

To minimize false signals, the strategy requires multiple layers of verification:

### ✅ Signal Generation Criteria

**🟢 BUY Signal** (All conditions required):
```
├─ RSI < 40 (oversold but not panic)
├─ MACD Bullish (MACD line > Signal line)
├─ Volume > Volume SMA (20-period)
├─ Previous Bar Confirmation (prev RSI < 45 AND prev MACD bullish)
├─ Divergence OR H4 Trend (Bullish Divergence detected OR H4 > SMA50)
├─ H4 RSI Guard: H4 RSI < 65 (not overbought on higher timeframe)
└─ Macro Regime: NOT in BEAR (SMA50 > SMA200 on H4)
```

**🔴 SELL Signal** (All conditions required):
```
├─ RSI > 60 (overbought but not panic)
├─ MACD Bearish (MACD line < Signal line)
├─ Volume > Volume SMA (20-period)
├─ Previous Bar Confirmation (prev RSI > 55 AND prev MACD bearish)
├─ Divergence OR H4 Trend (Bearish Divergence detected OR H4 < SMA50)
├─ H4 RSI Guard: H4 RSI > 35 (not oversold on higher timeframe)
└─ Macro Regime: NOT in BULL (SMA50 < SMA200 on H4)
```

**⏱️ HOLD Signal**:
- Default state when not all BUY/SELL conditions are met.
- Can have HIGH confluence and winrate while waiting for optimal entry conditions.
- Example: BNB with 85% confidence + 62% winrate staying in HOLD = market strength confirmed, but entry filters active.

### 📊 Confidence Score Breakdown
- **RSI Extreme (±15)**: RSI < 30 or > 70
- **RSI Near Extreme (±5)**: RSI < 40 or > 60
- **RSI Divergence (±25)**: Bullish/Bearish divergence detected
- **MACD + SMA20 (±15)**: MACD bullish AND price > SMA20
- **H4 Trend Alignment (±20)**: H4 trend matches signal direction
- **Volume Validation (±15)**: Volume > Volume SMA
- **Trend Confluence (±10)**: SMA20 > SMA50 (uptrend)

**Total: 0-100 (capped)**

### 📈 Winrate Calculation
- **Window**: Last 200 candles (200 hours of 1h data)
- **Trade Simulation**: Tests RSI/MACD confluence at each bar, checks if next 2 hours profitable
- **Formula**: (Winning Trades / Total Confluence Instances) × 100
- **Fallback**: If no confluence found, uses volatility-based estimate

## 🔧 Endpoints

### WebSocket
- `WS /ws` - Real-time ticker data (2s updates)
  ```json
  {
    "BTCUSDT": {"price": 43250.50, "signal": "BUY", "confidence": 78.5, "winrate": 62.3, ...},
    "ETHUSDT": {"price": 2280.75, "signal": "HOLD", "confidence": 85.0, "winrate": 68.9, ...},
    "SOLUSDT": {"price": 142.30, "signal": "SELL", "confidence": 71.2, "winrate": 59.5, ...},
    "BNBUSDT": {"price": 612.45, "signal": "HOLD", "confidence": 86.1, "winrate": 64.7, ...}
  }
  ```

### REST API
- `GET /api/health` - Health check (uptime monitoring)
- `POST /api/webhook` - Set Discord webhook URL
- `GET /api/webhook` - Get current webhook
- `POST /api/trade` - Execute manual order (requires Binance API key/secret)
- `GET /api/history` - Trade execution history
- `GET /api/signals` - Signal change history

## 📊 Example Signal States
```json
{
  "SOLUSDT": {
    "price": 142.30,
    "signal": "BUY",
    "confidence": 76.5,
    "winrate": 63.2,
    "states": {
      "rsi": "OVERSOLD",
      "macd": "BULLISH",
      "sma_20": "BELOW",
      "sma_50": "BELOW",
      "trend": "BEARISH",
      "divergence": "BULLISH",
      "volume": "HIGH",
      "h4_trend": "BULLISH",
      "h4_rsi": 42.5,
      "macro_regime": "BULL"
    }
  }
}
```

## 🚀 Deployment

### Local (RPi5)
```bash
cd /home/artware/.hermes/hermes-agent/crypto-dashboard
docker-compose up -d
```

### Remote (Tailscale)
```
Frontend: https://crypto.chantilly-shaula.ts.net
Backend: http://localhost:8000 (internal)
```

## 🐛 Troubleshooting

### WebSocket Reconnection Issues
- Check browser console for errors
- Verify backend is running: `docker logs crypto-dashboard-backend-1`
- Ensure firewall allows WebSocket traffic

### Signal Not Updating
- Backend may be fetching data from Binance API (30s cycle)
- Check if Binance API is accessible: `curl https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT`

### Discord Webhook Not Working
- Verify webhook URL in settings
- Check Discord server permissions for the bot webhook

## 📝 Development Notes

### Adding a New Asset
1. Add symbol to `tickers_data` dict in `main.py` (line 73-78)
2. Add to `previous_signals` dict (line 64)
3. Add `<TickerCard symbol="NEW/USDT" data={...} />` in `App.jsx`
4. Ensure Binance supports the symbol

### Backtesting
```bash
docker exec crypto-dashboard-backend-1 python3 backtest_full.py
```

## ⚖️ License
MIT - Developed with ❤️ for Artware.

---

**Last Updated:** 2026-04-06  
**Version:** 1.9.0  
**Status:** Production Ready ✅
