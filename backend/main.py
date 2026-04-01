import asyncio
import os
import json
import httpx
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from binance import AsyncClient, BinanceSocketManager
from pydantic import BaseModel
from logic import calculate_indicators, generate_signal_data

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
        allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Persistent Config (Webhook & History)
CONFIG_FILE = "config.json"
HISTORY_FILE = "trade_history.json"
SIGNAL_HISTORY_FILE = "signal_history.json"

def load_json(path):
    if os.path.exists(path):
        try:
            with open(path, "r") as f: return json.load(f)
        except: return [] if "history" in path else ({} if "config" in path else [])
    return [] if "history" in path else ({} if "config" in path else [])

def save_json(path, data):
    with open(path, "w") as f: json.dump(data, f)

# State Management
app_config = load_json(CONFIG_FILE)
app_history = load_json(HISTORY_FILE)
sig_history_init = load_json(SIGNAL_HISTORY_FILE)
previous_signals = {"BTCUSDT": "HOLD", "ETHUSDT": "HOLD"}

# Initialize previous_signals from history if available
for symbol in previous_signals:
    for entry in sig_history_init:
        if entry["symbol"] == symbol:
            previous_signals[symbol] = entry["new_signal"]
            break

tickers_data: Dict[str, Any] = {
    "BTCUSDT": {"price": 0.0, "change": 0.0, "signal": "HOLD", "timeframe": "1h", "market": "Spot"},
    "ETHUSDT": {"price": 0.0, "change": 0.0, "signal": "HOLD", "timeframe": "1h", "market": "Spot"},
}

class WebhookRequest(BaseModel): url: str
class TradeRequest(BaseModel):
    api_key: str
    api_secret: str
    symbol: str
    side: str
    quantity: float

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_tickers_and_signals())

async def send_discord_alert(symbol, old_signal, new_signal, price):
    url = app_config.get("discord_webhook")
    if not url: return
    color = 65280 if new_signal == "BUY" else (16711680 if new_signal == "SELL" else 8421504)
    emoji = "🚀" if new_signal == "BUY" else ("🔻" if new_signal == "SELL" else "⏱️")
    payload = {
        "embeds": [{
            "title": f"{emoji} Signal Changed: {symbol}",
            "description": f"Le signal est passé de **{old_signal}** à **{new_signal}**.",
            "color": color,
            "fields": [
                {"name": "Price", "value": f"${price:,.2f}", "inline": True},
                {"name": "Market", "value": "Spot", "inline": True}
            ],
            "timestamp": datetime.utcnow().isoformat()
        }]
    }
    async with httpx.AsyncClient() as client:
        try: await client.post(url, json=payload)
        except: pass

async def update_tickers_and_signals():
    client = await AsyncClient.create()
    try:
        while True:
            for symbol in ["BTCUSDT", "ETHUSDT"]:
                try:
                    # Fetch Variations (4h, 8h)
                    klines_4h = await client.get_klines(symbol=symbol, interval=AsyncClient.KLINE_INTERVAL_4HOUR, limit=2)
                    klines_8h = await client.get_klines(symbol=symbol, interval=AsyncClient.KLINE_INTERVAL_8HOUR, limit=2)
                    
                    def get_change(klines):
                        if len(klines) < 2: return 0.0
                        prev_close = float(klines[0][4])
                        curr_price = float(klines[1][4])
                        return ((curr_price / prev_close) - 1) * 100

                    change_4h = get_change(klines_4h)
                    change_8h = get_change(klines_8h)

                    # Fetch 1h klines for technical signals
                    klines = await client.get_klines(symbol=symbol, interval=AsyncClient.KLINE_INTERVAL_1HOUR, limit=250)
                    df = pd.DataFrame(klines, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'q_vol', 'no_trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
                    df[['close', 'volume']] = df[['close', 'volume']].astype(float)
                    
                    # Fetch 4h klines for trend filtering
                    klines_h4_full = await client.get_klines(symbol=symbol, interval=AsyncClient.KLINE_INTERVAL_4HOUR, limit=100)
                    h4_df = pd.DataFrame(klines_h4_full, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'q_vol', 'no_trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
                    h4_df[['close', 'volume']] = h4_df[['close', 'volume']].astype(float)

                    change_1h = 0.0
                    if len(df) >= 2:
                        change_1h = ((df['close'].iloc[-1] / df['close'].iloc[-2]) - 1) * 100
                    
                    df = calculate_indicators(df)
                    signal, confidence, winrate, states = generate_signal_data(df, h4_df=h4_df)
                    ticker = await client.get_ticker(symbol=symbol)
                    price = float(ticker['lastPrice'])
                    
                    if signal != previous_signals[symbol]:
                        old_sig = previous_signals[symbol]
                        await send_discord_alert(symbol, old_sig, signal, price)
                        previous_signals[symbol] = signal
                        
                        # Record Signal Change in History
                        sig_entry = {
                            "timestamp": datetime.now().isoformat(),
                            "symbol": symbol,
                            "old_signal": old_sig,
                            "new_signal": signal,
                            "price": price
                        }
                        sig_history = load_json(SIGNAL_HISTORY_FILE)
                        sig_history.insert(0, sig_entry)
                        save_json(SIGNAL_HISTORY_FILE, sig_history[:100]) # Keep last 100 entries
                    
                    tickers_data[symbol] = {
                        "market": "Spot", "timeframe": "1h", "price": price,
                        "change": float(ticker['priceChangePercent']), 
                        "changes": {"1h": change_1h, "4h": change_4h, "8h": change_8h, "24h": float(ticker['priceChangePercent'])}, 
                        "signal": signal,
                        "confidence": confidence, "winrate": winrate, "states": states,
                    }
                    if not df.empty and len(df) > 0 and 'rsi' in df.columns:
                        tickers_data[symbol].update({
                            "rsi": float(df['rsi'].iloc[-1]), 
                            "macd": float(df['MACD_12_26_9'].iloc[-1]),
                            "sma_20": float(df['sma_20'].iloc[-1]), 
                            "sma_50": float(df['sma_50'].iloc[-1]),
                        })
                except Exception as e:
                    print(f'Error updating {symbol}: {e}')
            await asyncio.sleep(10)
    finally: await client.close_connection()

@app.post("/api/webhook")
async def set_webhook(req: WebhookRequest):
    app_config["discord_webhook"] = req.url
    save_json(CONFIG_FILE, app_config)
    return {"status": "success"}

@app.get("/api/webhook")
async def get_webhook(): return {"url": app_config.get("discord_webhook", "")}

@app.websocket("/ws/tickers")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(tickers_data)
            await asyncio.sleep(2)
    except WebSocketDisconnect: pass

@app.get("/api/history")
async def get_trade_history(): return load_json(HISTORY_FILE)

@app.get("/api/signals")
async def get_signal_history(): return load_json(SIGNAL_HISTORY_FILE)

@app.post("/api/trade")
async def execute_trade(request: TradeRequest):
    try:
        client = await AsyncClient.create(request.api_key, request.api_secret)
        if request.side.upper() == "BUY":
            order = await client.order_market_buy(symbol=request.symbol.upper(), quantity=request.quantity)
        elif request.side.upper() == "SELL":
            order = await client.order_market_sell(symbol=request.symbol.upper(), quantity=request.quantity)
        else: raise HTTPException(status_code=400, detail="Invalid side.")
        
        entry = {
            "timestamp": datetime.now().isoformat(), "symbol": request.symbol.upper(),
            "side": request.side.upper(), "quantity": request.quantity, "status": "FILLED",
            "price": float(order.get('fills', [{}])[0].get('price', 0)) if order.get('fills') else 0
        }
        history = load_json(HISTORY_FILE)
        history.insert(0, entry)
        save_json(HISTORY_FILE, history[:50])
        await client.close_connection()
        return {"status": "success", "order": order}
    except Exception as e:
        entry = {"timestamp": datetime.now().isoformat(), "symbol": request.symbol.upper(), "side": request.side.upper(), "quantity": request.quantity, "status": "FAILED", "error": str(e)}
        history = load_json(HISTORY_FILE)
        history.insert(0, entry)
        save_json(HISTORY_FILE, history[:50])
        return {"status": "error", "message": str(e)}

@app.get("/api/health")
async def health_check(): return {"status": "ok"}
