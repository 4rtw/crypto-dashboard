# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A real-time crypto trading surveillance dashboard for Binance Spot (BTC/USDT, ETH/USDT, SOL/USDT, BNB/USDT). Backend is Python FastAPI; frontend is React + Vite + Tailwind CSS. Deployed via Docker Compose.

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
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger) or `/redoc`.

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
# In-container (Production)
docker exec crypto-dashboard-backend-1 python3 backtest_full.py

# Local
cd backend
python backtest_cli.py     # Quick backtest
python backtest_full.py    # Extended backtest with full metrics
```

There are no lint or test scripts configured.

## Architecture

### Data Flow
1. `main.py` runs a background async loop (`update_tickers_and_signals`) that fetches Binance klines every 10 seconds and calls `logic.py` to compute signals.
2. Results are broadcast to all connected frontend clients via WebSocket (`/ws`) every 2 seconds.
3. On signal transitions (HOLD→BUY, BUY→SELL, etc.), Discord embeds are sent and the change is written to `signal_history.json`.
4. The frontend `useBinanceSocket.js` hook manages the WebSocket connection; components poll `/api/history` and `/api/signals` every 5 seconds for persistent history.

### Backend (`backend/`)
- **`main.py`** — FastAPI app, WebSocket endpoint, REST endpoints, in-memory state (`tickers_data`, `previous_signals`), JSON persistence
- **`logic.py`** — Signal generation: RSI/MACD/SMA/divergence computation via `pandas-ta`, multi-timeframe confluence, confidence scoring (0–100), winrate calculation (last 200 bars)

**Key REST endpoints:**
| Method | Path | Purpose |
|--------|------|---------|
| WS | `/ws` | Real-time ticker stream |
| POST | `/api/trade` | Execute Binance market order |
| POST/GET | `/api/webhook` | Discord webhook URL |
| GET | `/api/history` | Trade execution history |
| GET | `/api/signals` | Signal change history |

**Persistent files** (auto-created, not in git):
- `backend/config.json` — Discord webhook URL
- `backend/signal_history.json` — Last 100 signal transitions
- `backend/trade_history.json` — Last 50 trade executions

### Frontend (`frontend/src/`)
- **`App.jsx`** — 2x2 grid layout; holds WebSocket state
- **`hooks/useBinanceSocket.js`** — WebSocket lifecycle, reconnect logic (every 5s)
- **`components/TickerCard.jsx`** — Main signal display (price, RSI, MACD, confidence, winrate, H4 trend)
- **`components/TradeForm.jsx`** — Binance API key/secret order form (keys never stored)

### Adding a New Asset
1. Add symbol to `tickers_data` and `previous_signals` in `backend/main.py`.
2. Add `<TickerCard symbol="NEW/USDT" ... />` in `frontend/src/App.jsx`.

## Trading Strategy (logic.py)

**BUY Signal (All required):**
- RSI < 40 + Bullish MACD crossover
- Volume > SMA20 + 2-bar confirmation
- (Bullish RSI divergence OR H4 trend > SMA50)
- H4 RSI < 65 + Macro Regime (NOT BEAR: SMA50 > SMA200 on H4)

**SELL Signal (All required):**
- RSI > 60 + Bearish MACD crossover
- Volume > SMA20 + 2-bar confirmation
- (Bearish RSI divergence OR H4 trend < SMA50)
- H4 RSI > 35 + Macro Regime (NOT BULL: SMA50 < SMA200 on H4)

**Confidence Score (0–100):** Weights for RSI extremes (±15/5), RSI divergence (±25), MACD + SMA20 (±15), H4 trend alignment (±20), volume validation (±15), trend confluence (±10).
