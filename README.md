# 🚀 Enhanced Binance Crypto Dashboard (Spot)

A production-ready, high-performance crypto trading and surveillance dashboard for **BTC/USDT** and **ETH/USDT** Spot markets on Binance.

![Platform](https://img.shields.io/badge/Market-Binance%20Spot-blue)
![Timeframe](https://img.shields.io/badge/Timeframe-1h-green)
![Tech](https://img.shields.io/badge/Stack-FastAPI%20%2B%20React-orange)

## ✨ New Features (V1.2)
-   **📈 Confluence & Confidence Scoring**: Calculates a confidence score (%) based on the agreement of multiple technical indicators (RSI, MACD, SMA 20/50).
-   **🛡️ Dynamic Winrate Backtester**: Performs a background 1-hour backtest on the last 30 days of data to provide a statistical probability of success for current signals.
-   **🔔 Discord Webhook Integration**: Get instant notifications in your Discord channel whenever a signal changes (BUY/SELL/HOLD). 
-   **📜 Persistent Trade History**: Local tracking of all executed orders (Spot only), including FILLED or FAILED status, execution price, and quantity.
-   **💎 Modern Trading UI**: Enhanced dashboard with real-time WebSocket updates, progress bars for winrate/confidence, and individual indicator states.
-   **🔒 Security-First**: API keys are passed per-transaction from the UI and never stored on the server side (non-persistent state).

## 🛠️ Tech Stack
-   **Frontend:** React (Vite), Tailwind CSS, Lucide Icons, Fetch API.
-   **Backend:** FastAPI, `python-binance` (Async), `pandas_ta`, `httpx` (for webhooks).
-   **Infrastructure:** Docker & Docker Compose (Containerized).
-   **Real-time:** WebSockets for instant ticker and indicator transmission.

## 📁 Project Structure
```text
crypto-dashboard/
├── backend/
│   ├── main.py        - FastAPI entrypoint & Discord Notification logic
│   ├── logic.py       - Trading Strategy, Signals & Backtest Winrate logic
│   ├── backtest_cli.py- Standalone CLI for 30-day historical strategy analysis
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/ - TickerCard, TradeForm, TradeHistory, NotificationSettings
│   │   ├── hooks/      - WebSocket state management
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
1.  **Monitor**: View BTC and ETH price action, RSI (14), MACD (12,26,9), and SMA (20,50) states in real-time.
2.  **Alerts**: Paste your Discord Webhook URL in the "Alerts" section to receive signal change notifications.
3.  **Trade**: Input your Binance API Key and Secret in the "Execute Order" form to place SPOT market orders instantly.
4.  **Backtest**: You can run the standalone backtest script to see performance over 30 days:
    ```bash
    docker compose run --rm backend python3 backtest_cli.py
    ```

## 🧠 Strategy Logic (Confluence)
-   **BUY Signal**: RSI < 35 + Bullish MACD Crossover.
-   **SELL Signal**: RSI > 65 + Bearish MACD Crossover.
-   **Confidence Score**: Weighted based on alignment between price position (vs SMAs), Oscillator extremes, and Trend momentum.

## ⚖️ License
MIT - Developed with ❤️ for Artware.
