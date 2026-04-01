import asyncio
import pandas as pd
import sys
import os
import json
import numpy as np
from binance import AsyncClient
from logic import calculate_indicators, detect_rsi_divergence, generate_signal_data

async def main():
    client = await AsyncClient.create()
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "TAOUSDT", "FETUSDT", "DOGEUSDT"]
    
    results = {}
    
    print(f"{'Symbol':<10} | {'Price':<10} | {'SMA20':<12} | {'SMA50':<12} | {'RSI':<6} | {'Trend':<8} | {'H4 Trend':<8}")
    print("-" * 100)
    
    for symbol in symbols:
        try:
            # H1 Data
            try:
                k1h = await client.get_klines(symbol=symbol, interval=AsyncClient.KLINE_INTERVAL_1HOUR, limit=200)
            except Exception as e:
                print(f"{symbol:<10} | Error fetching: {e}")
                continue
                
            df = pd.DataFrame(k1h, columns=['time','open','high','low','close','volume','ct','qv','nt','tb','tq','i'])
            for c in ['open','high','low','close','volume']:
                df[c] = pd.to_numeric(df[c], errors='coerce').astype(float)
            
            # H4 Trend Data
            kh4 = await client.get_klines(symbol=symbol, interval=AsyncClient.KLINE_INTERVAL_4HOUR, limit=200)
            h4_df = pd.DataFrame(kh4, columns=['time','open','high','low','close','volume','ct','qv','nt','tb','tq','i'])
            for c in ['open','high','low','close','volume']:
                h4_df[c] = pd.to_numeric(h4_df[c], errors='coerce').astype(float)
            
            df = calculate_indicators(df)
            sig, conf, win, states = generate_signal_data(df, h4_df=h4_df)
            
            px = float(df['close'].iloc[-1])
            sma20 = float(df['sma_20'].iloc[-1]) if 'sma_20' in df.columns else 0
            sma50 = float(df['sma_50'].iloc[-1]) if 'sma_50' in df.columns else 0
            rsi = float(df['rsi'].iloc[-1]) if 'rsi' in df.columns else 0
            trend = states.get("trend", "N/A")
            h4_trend = states.get("h4_trend", "N/A")
            
            print(f"{symbol:<10} | {px:<10.2f} | {sma20:<12.2f} | {sma50:<12.2f} | {rsi:<6.1f} | {trend:<8} | {h4_trend:<8}")
            
        except Exception as e:
            print(f"{symbol:<10} | Error: {e}")
            
    await client.close_connection()

if __name__ == "__main__":
    asyncio.run(main())
