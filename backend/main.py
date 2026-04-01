import numpy as np
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



def json_safe(data):
    if isinstance(data, dict):
        return {k: json_safe(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [json_safe(v) for v in data]
    elif isinstance(data, float):
        if np.isnan(data) or np.isinf(data): return 0.0
        return float(round(data, 4))
    return data

def sanitize_float(val):
    try:
        f = float(val)
        if pd.isna(f) or np.isinf(f): return 0.0
        return f
    except: return 0.0

def save_json(path, data):
    with open(path, "w") as f: json.dump(data, f)

# State Management
app_config = load_json(CONFIG_FILE)
app_history = load_json(HISTORY_FILE)
sig_history_init = load_json(SIGNAL_HISTORY_FILE)
previous_signals = {"BTCUSDT": "HOLD", "ETHUSDT": "HOLD", "SOLUSDT": "HOLD", "BNBUSDT": "HOLD"}

# Initialize previous_signals from history if available
for symbol in previous_signals:
    for entry in sig_history_init:
        if entry["symbol"] == symbol:
            previous_signals[symbol] = entry["new_signal"]
            break

tickers_data: Dict[str, Any] = {
    "BTCUSDT": {"price": 0.0, "change": 0.0, "signal": "HOLD", "timeframe": "1h", "market": "Spot"},
    "ETHUSDT": {"price": 0.0, "change": 0.0, "signal": "HOLD", "timeframe": "1h", "market": "Spot"},
    "SOLUSDT": {"price": 0.0, "change": 0.0, "signal": "HOLD", "timeframe": "1h", "market": "Spot"},
    "BNBUSDT": {"price": 0.0, "change": 0.0, "signal": "HOLD", "timeframe": "1h", "market": "Spot"},
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
            for symbol in ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]:
                try:
                    # Variations 4h, 8h (quick check)
                    k4h = await client.get_klines(symbol=symbol, interval=AsyncClient.KLINE_INTERVAL_4HOUR, limit=2)
                    k8h = await client.get_klines(symbol=symbol, interval=AsyncClient.KLINE_INTERVAL_8HOUR, limit=2)
                    
                    def get_change(ks):
                        if len(ks) < 2: return 0.0
                        return ((float(ks[1][4]) / float(ks[0][4])) - 1) * 100
                    
                    c4h, c8h = get_change(k4h), get_change(k8h)

                    # H1 Core Data
                    k1h = await client.get_klines(symbol=symbol, interval=AsyncClient.KLINE_INTERVAL_1HOUR, limit=250)
                    df = pd.DataFrame(k1h, columns=['time','open','high','low','close','volume','ct','qv','nt','tb','tq','i'])
                    for c in ['open','high','low','close','volume']:
                        df[c] = pd.to_numeric(df[c], errors='coerce').astype(float)
                    
                    # H4 Trend Data
                    kh4 = await client.get_klines(symbol=symbol, interval=AsyncClient.KLINE_INTERVAL_4HOUR, limit=250)
                    h4_df = pd.DataFrame(kh4, columns=['time','open','high','low','close','volume','ct','qv','nt','tb','tq','i'])
                    for c in ['open','high','low','close','volume']:
                        h4_df[c] = pd.to_numeric(h4_df[c], errors='coerce').astype(float)

                    c1h = 0.0
                    if len(df) >= 2:
                        c1h = ((df['close'].iloc[-1] / df['close'].iloc[-2]) - 1) * 100
                    
                    df = calculate_indicators(df)
                    sig, conf, win, states = generate_signal_data(df, h4_df=h4_df)
                    
                    tick = await client.get_ticker(symbol=symbol)
                    px = sanitize_float(tick['lastPrice'])
                    
                    if sig != previous_signals[symbol]:
                        old = previous_signals[symbol]
                        await send_discord_alert(symbol, old, sig, px)
                        previous_signals[symbol] = sig
                        
                        entry = {
                            "timestamp": datetime.now().isoformat(),
                            "symbol": symbol, "old_signal": old, "new_signal": sig, "price": px
                        }
                        sh = load_json(SIGNAL_HISTORY_FILE)
                        sh.insert(0, entry)
                        save_json(SIGNAL_HISTORY_FILE, sh[:100])
                    
                    tickers_data[symbol] = {
                        "market": "Spot", "timeframe": "1h", "price": px,
                        "change": sanitize_float(tick['priceChangePercent']),
                        "changes": {"1h": c1h, "4h": c4h, "8h": c8h, "24h": sanitize_float(tick['priceChangePercent'])},
                        "signal": sig, "confidence": conf, "winrate": win, "states": states,
                        "rsi": sanitize_float(df['rsi'].iloc[-1]) if 'rsi' in df.columns and not pd.isna(df['rsi'].iloc[-1]) else 0,
                        "macd": sanitize_float(df['MACD_12_26_9'].iloc[-1]) if 'MACD_12_26_9' in df.columns and not pd.isna(df['MACD_12_26_9'].iloc[-1]) else 0,
                        "sma_20": sanitize_float(df['sma_20'].iloc[-1]) if 'sma_20' in df.columns and not pd.isna(df['sma_20'].iloc[-1]) else 0,
                        "sma_50": sanitize_float(df['sma_50'].iloc[-1]) if 'sma_50' in df.columns and not pd.isna(df['sma_50'].iloc[-1]) else 0,
                    }
                except Exception as e:
                    print(f"Error updating {symbol}: {e}")
            await asyncio.sleep(10)
    finally: await client.close_connection()

@app.post("/api/webhook")
async def set_webhook(req: WebhookRequest):
    app_config["discord_webhook"] = req.url
    save_json(CONFIG_FILE, app_config)
    return {"status": "success"}

@app.get("/api/webhook")
async def get_webhook(): return {"url": app_config.get("discord_webhook", "")}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(json_safe(tickers_data))
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
