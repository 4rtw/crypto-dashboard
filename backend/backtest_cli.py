import pandas as pd
import pandas_ta as ta
import numpy as np
from binance import Client
import os
import json

def calculate_indicators(df):
    if df.empty: return df
    df['rsi'] = ta.rsi(df['close'], length=14)
    macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
    df = pd.concat([df, macd], axis=1)
    df['sma_20'] = ta.sma(df['close'], length=20)
    df['sma_50'] = ta.sma(df['close'], length=50)
    return df

def run_backtest(symbol, days=30):
    client = Client() # Public API doesn't need keys for klines
    # print(f"Fetching {days} days of 1h data for {symbol}...")
    klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1HOUR, f"{days} day ago UTC")
    
    df = pd.DataFrame(klines, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'q_vol', 'no_trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = df[col].astype(float)
    
    df = calculate_indicators(df)
    df.dropna(inplace=True)
    
    # Strategy from logic.py
    # BUY: rsi < 35 and macd > signal
    # SELL: rsi > 65 and macd < signal
    
    position = 0 
    entry_price = 0
    trades = []
    
    for i in range(1, len(df)):
        row = df.iloc[i]
        rsi = row['rsi']
        # Looking at columns produced by pandas-ta MACD: MACD_12_26_9, MACDs_12_26_9
        # These are generated as: MACD_12_26_9 (macd line) AND MACDs_12_26_9 (signal line)
        macd_line = row['MACD_12_26_9']
        macd_signal = row['MACDs_12_26_9']
        price = row['close']
        
        if position == 0:
            if rsi < 35 and macd_line > macd_signal:
                position = 1
                entry_price = price
        
        elif position == 1:
            if rsi > 70 or (rsi > 65 and macd_line < macd_signal): # EXIT: Overbought or MACD bearish
                profit = (price - entry_price) / entry_price
                trades.append(profit)
                position = 0

    if not trades:
        return {"symbol": symbol, "total_trades": 0, "winrate": 0, "profit": 0}

    wins = [t for t in trades if t > 0]
    losses = [t for t in trades if t <= 0]
    winrate = len(wins) / len(trades) * 100
    cum_profit = (np.prod([1 + t for t in trades]) - 1) * 100
    
    return {
        "symbol": symbol,
        "total_trades": len(trades),
        "winrate": round(winrate, 2),
        "total_perf": round(cum_profit, 2),
        "avg_trade": round(sum(trades)/len(trades)*100, 2),
        "best_trade": round(max(trades)*100, 2) if trades else 0,
        "worst_trade": round(min(trades)*100, 2) if trades else 0
    }

if __name__ == "__main__":
    results = []
    for sym in ["BTCUSDT", "ETHUSDT"]:
        try:
            res = run_backtest(sym, days=30)
            results.append(res)
        except Exception as e:
            results.append({"symbol": sym, "error": str(e)})
    
    print("BACKTEST_RESULTS")
    print(json.dumps(results, indent=2))
