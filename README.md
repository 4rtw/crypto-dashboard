# 🚀 Enhanced Binance Crypto Dashboard (Spot)

A production-ready, high-performance crypto trading and surveillance dashboard for **BTC/USDT** and **ETH/USDT** Spot markets on Binance.

![Platform](https://img.shields.io/badge/Market-Binance%20Spot-blue)
![Timeframe](https://img.shields.io/badge/Timeframe-1h%2F4h%2F8h-green)
![Tech](https://img.shields.io/badge/Stack-FastAPI%20%2B%20React-orange)

## ✨ New Features (V1.7)
-   **🎯 Advanced Strategy Confluences**:
    -   **🛡️ RSI Divergence Detection**: Identifies Bullish/Bearish divergences between price and RSI for high-conviction entries.
    -   **📊 Volume Validation**: Signals are now filtered by volume spikes relative to a 20-period Simple Moving Average.
    -   **📡 H4 Trend Filtering**: Integrates a higher-timeframe filter (H4 SMA 50) to ensure signals align with the broader market direction.
-   **🛡️ Data Integrity & Stability**:
    -   **Recursive JSON Sanitizer**: Global backend protection against `NaN` and `Infinity` values, preventing silent WebSocket crashes.
    -   **Auto-Reconnect Hook**: Frontend WebSocket logic that automatically reconnects every 5 seconds in case of network drops or server restarts.
    -   **Bulletproof Calculations**: Technical indicators now include explicit type casting and corrupted data dropping for maximum reliability.
-   **📈 Extended Multi-Timeframe Variations**: Real-time tracking of price changes across **1h, 4h, 8h, and 24h** intervals (deprecated noisy 5m/15m charts).
-   **📜 Persistent Signal History**: Dedicated UI panel and local storage (`signal_history.json`) to track and persist every signal change (HOLD/BUY/SELL) with price and timestamps.
-   **🛠️ Robust Monitoring Loop**: Enhanced background tasks with per-crypto error isolation to ensure one asset's downtime doesn't affect the entire dashboard.

## 🛠️ Tech Stack
-   **Frontend:** React (Vite), Tailwind CSS, Lucide Icons, Fetch API.
-   **Backend:** FastAPI, `python-binance` (Async), `pandas_ta`, `httpx` (for webhooks).
-   **Infrastructure:** Docker & Docker Compose (Containerized).
-   **Real-time:** WebSockets for instant ticker and indicator transmission.

## 📁 Project Structure
```text
crypto-dashboard/
├── backend/
│   ├── main.py        - FastAPI entrypoint & Persistent history logic
│   ├── logic.py       - RSI Divergence, Strategy Confluences & H4 Filtering
│   ├── signal_history.json - Persistent signal changes
│   ├── trade_history.json  - Persistent execution logs
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/ - TickerCard, SignalHistory, TradeHistory, TradeForm
│   │   ├── hooks/      - WebSocket (Auto-reconnect) & Polling management
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🚀 Setup & Operation

### 1. Prerequisites
-   [Docker](https://www.docker.com/) installed on your machine.

### 2. Quick Launch
From the `crypto-dashboard/` root directory:
```bash
docker-compose up --build
```
-   **Dashboard:** [http://localhost:5173](http://localhost:5173)
-   **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Usage
1.  **Monitor**: View BTC/ETH price action alongside **Advanced Analysis** (Divergence, Volume, H4 Trend).
2.  **History**: Scroll down to see the **Signal History** (why the bot changed status) and **Execution History** (actual trades).
3.  **Alerts**: Paste your Discord Webhook URL in the "Alerts" section to receive instant signal notifications.
4.  **Trade**: Input your Binance API Key and Secret in the "Execute Order" form for manual Spot orders.

## 🧠 Strategy Logic (V1.7 Confluence)
To minimize false signals and "noise", the strategy now requires multiple layers of verification:
-   **BUY Signal**: H1 RSI < 40 + Bullish MACD + (Bullish Divergence OR H4 Bullish Trend) + Volume > Volume SMA.
-   **SELL Signal**: H1 RSI > 60 + Bearish MACD + (Bearish Divergence OR H4 Bearish Trend) + Volume > Volume SMA.
-   **Confidence Score**: Maximum weight given to **Divergences (+25)** and **H4 Trend Alignment (+20)**.

## ⚖️ License
MIT - Developed with ❤️ for Artware.
