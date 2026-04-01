# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A real-time crypto trading surveillance dashboard for Binance Spot (BTC/USDT, ETH/USDT). Backend is Python FastAPI; frontend is React + Vite + Tailwind CSS. Deployed via Docker Compose.

## Common Commands

### Docker (primary workflow)
```bash
docker-compose up --build        # Start everything
docker-compose up                # Start without rebuilding
docker-compose down              # Stop
```

### Backend (local dev)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (local dev)
```bash
cd frontend
npm install
npm run dev       # Dev server with HMR
npm run build     # Production build
npm run preview   # Preview production build
```

### Backtesting
```bash
cd backend
python backtest_cli.py     # Quick backtest
python backtest_full.py    # Extended backtest with full metrics
```

There are no lint or test scripts configured.

## Architecture

### Data Flow
1. `main.py` runs a background async loop (`update_tickers_and_signals`) that fetches Binance klines every 10 seconds and calls `logic.py` to compute signals.
2. Results are broadcast to all connected frontend clients via WebSocket (`/ws/tickers`) every 2 seconds.
3. On signal transitions (HOLD→BUY, BUY→SELL, etc.), Discord embeds are sent and the change is written to `signal_history.json`.
4. The frontend `useBinanceSocket.js` hook manages the WebSocket connection; components poll `/api/history` and `/api/signals` every 5 seconds for persistent history.

### Backend (`backend/`)
- **`main.py`** — FastAPI app, WebSocket endpoint, REST endpoints, in-memory state (`tickers_data`, `previous_signals`), JSON persistence
- **`logic.py`** — All signal generation: RSI/MACD/SMA/divergence computation via `pandas-ta`, multi-timeframe confluence, confidence scoring (0–100), winrate calculation (backtested over last 200 bars)

**Key REST endpoints:**
| Method | Path | Purpose |
|--------|------|---------|
| WS | `/ws/tickers` | Real-time ticker stream |
| POST | `/api/trade` | Execute Binance market order |
| POST/GET | `/api/webhook` | Discord webhook URL |
| GET | `/api/history` | Trade execution history |
| GET | `/api/signals` | Signal change history |

**Persistent files** (auto-created, not in git):
- `backend/config.json` — Discord webhook URL
- `backend/signal_history.json` — Last 100 signal transitions
- `backend/trade_history.json` — Last 50 trade executions

### Frontend (`frontend/src/`)
- **`App.jsx`** — Layout and component orchestration; holds WebSocket state
- **`hooks/useBinanceSocket.js`** — WebSocket lifecycle, reconnect logic, bidirectional messaging
- **`components/TickerCard.jsx`** — Main signal display (price, RSI, MACD, confidence, winrate, H4 trend)
- **`components/TradeForm.jsx`** — API key/secret + order form; keys are never stored, only passed to backend per request

### Vite Proxy (dev)
`vite.config.js` proxies `/api` → `http://backend:8000` and `/ws` → `ws://backend:8000`, so frontend calls `fetch('/api/...')` without hardcoded ports.

## Trading Strategy (logic.py)

**BUY signal requires all:** RSI < 40 + Bullish MACD crossover + (Bullish RSI divergence OR H4 bullish trend) + Volume > SMA20 + 2-bar confirmation

**SELL signal requires all:** RSI > 60 + Bearish MACD crossover + (Bearish RSI divergence OR H4 bearish trend) + Volume > SMA20 + 2-bar confirmation

**Macro filter:** If H4 SMA50 vs SMA200 indicates BEAR regime, BUY signals are blocked (and vice versa for SELL in BULL regime).

**Confidence score** (0–100) adds weight for: RSI extremes (+5/+15), divergence (+25), H4 trend alignment (+20), MACD + SMA20 (+15), volume (+15), SMA confluence (+10).
