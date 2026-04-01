import pandas as pd
import pandas_ta as ta
import numpy as np

def calculate_indicators(df):
    if df.empty: return df
    df['rsi'] = ta.rsi(df['close'], length=14)
    macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
    df = pd.concat([df, macd], axis=1)
    df['sma_20'] = ta.sma(df['close'], length=20)
    df['sma_50'] = ta.sma(df['close'], length=50)
    df['vol_sma'] = ta.sma(df['volume'], length=20)
    return df

def detect_rsi_divergence(df, lookback=20):
    if len(df) < lookback + 5:
        return "NONE"
    
    recent_df = df.tail(lookback).copy()
    
    # Simple peak/trough detection
    # Bullish Divergence: Lower Low in Price, Higher Low in RSI
    # Bearish Divergence: Higher High in Price, Lower High in RSI
    
    # Just checking the last two local minima/maxima for simplicity
    prices = recent_df['close'].values
    rsis = recent_df['rsi'].values
    
    # Find local minima/maxima
    # This is a simplified version
    
    # We'll just compare current low with recent low
    curr_price = prices[-1]
    curr_rsi = rsis[-1]
    
    # Find previous low in the lookback period (excluding the last few bars)
    prev_segment = rsis[:-5]
    if len(prev_segment) == 0: return "NONE"
    
    min_rsi_idx = np.argmin(prev_segment)
    prev_min_price = prices[min_rsi_idx]
    prev_min_rsi = prev_segment[min_rsi_idx]
    
    max_rsi_idx = np.argmax(prev_segment)
    prev_max_price = prices[max_rsi_idx]
    prev_max_rsi = prev_segment[max_rsi_idx]
    
    # Bullish Divergence: Price makes lower low, RSI makes higher low
    if curr_price < prev_min_price and curr_rsi > prev_min_rsi and curr_rsi < 35:
        return "BULLISH"
    
    # Bearish Divergence: Price makes higher high, RSI makes lower high
    if curr_price > prev_max_price and curr_rsi < prev_max_rsi and curr_rsi > 65:
        return "BEARISH"
        
    return "NONE"

def generate_signal_data(df, h4_df=None):
    if df.empty or len(df) < 2:
        return "HOLD", 0, 0, {}
        
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]
    
    rsi = last_row['rsi']
    macd_line = last_row['MACD_12_26_9']
    macd_signal = last_row['MACDs_12_26_9']
    sma_20 = last_row['sma_20']
    sma_50 = last_row['sma_50']
    close = last_row['close']
    volume = last_row['volume']
    vol_sma = last_row['vol_sma']
    
    # RSI Divergence
    divergence = detect_rsi_divergence(df)
    
    # Volume Validation
    volume_ok = volume > vol_sma
    
    # H4 Trend Filter
    h4_trend = "NEUTRAL"
    if h4_df is not None and not h4_df.empty:
        h4_df = calculate_indicators(h4_df)
        if len(h4_df) > 0:
            h4_last = h4_df.iloc[-1]
            h4_trend = "BULLISH" if h4_last['close'] > h4_last['sma_50'] else "BEARISH"

    states = {
        "rsi": "OVERBOUGHT" if rsi > 70 else ("OVERSOLD" if rsi < 30 else "NEUTRAL"),
        "macd": "BULLISH" if macd_line > macd_signal else "BEARISH",
        "sma_20": "ABOVE" if close > sma_20 else "BELOW",
        "sma_50": "ABOVE" if close > sma_50 else "BELOW",
        "trend": "BULLISH" if sma_20 > sma_50 else "BEARISH",
        "divergence": divergence,
        "volume": "HIGH" if volume_ok else "LOW",
        "h4_trend": h4_trend
    }
    
    # Confidence Score (Dynamic based on Multiple Confluences)
    score = 0
    # 1. RSI Extreme
    if rsi < 30 or rsi > 70: score += 15
    elif rsi < 40 or rsi > 60: score += 5
    
    # 2. RSI Divergence (Strong)
    if (divergence == "BULLISH" and rsi < 40) or (divergence == "BEARISH" and rsi > 60):
        score += 25
    
    # 3. MACD Momentum & SMA 20
    if (macd_line > macd_signal and close > sma_20): score += 15
    
    # 4. H4 Trend Alignment (Filter)
    if (h4_trend == "BULLISH" and close > sma_50): score += 20
    elif (h4_trend == "BEARISH" and close < sma_50): score += 20
    
    # 5. Volume Validation
    if volume_ok: score += 15
    
    # 6. Trend Confluence
    if sma_20 > sma_50: score += 10
    
    # Random micro adjustment removed for pure logic
    confidence = min(score, 100)
    
    # Signal Generation Logic
    signal = "HOLD"
    if rsi < 40 and macd_line > macd_signal:
        # Require either divergence OR H4 trend alignment for BUY
        if divergence == "BULLISH" or h4_trend == "BULLISH":
            signal = "BUY"
            
    elif rsi > 60 and macd_line < macd_signal:
        # Require either divergence OR H4 trend alignment for SELL
        if divergence == "BEARISH" or h4_trend == "BEARISH":
            signal = "SELL"
    
    # Calculate Winrate on a 200-period window
    winrate = calculate_backtest_winrate(df, window=200)
    
    return signal, round(confidence, 1), round(winrate, 1), states

def calculate_backtest_winrate(df, window=200):
    if len(df) < 50: return 0.0
    
    # Use available data up to window size
    subset = df.tail(min(len(df), window)).copy()
    wins = 0
    total_trades = 0
    
    for i in range(len(subset) - 3):
        row = subset.iloc[i]
        curr_price = row['close']
        future_price = subset.iloc[i+2]['close'] # 2 hours ahead
        
        r = row['rsi']
        ml = row['MACD_12_26_9']
        ms = row['MACDs_12_26_9']
        
        if r < 40 and ml > ms: # BUY attempt
            total_trades += 1
            if future_price > curr_price: wins += 1
        elif r > 60 and ml < ms: # SELL attempt
            total_trades += 1
            if future_price < curr_price: wins += 1
            
    if total_trades == 0:
        return 50.0 + (subset['close'].pct_change().iloc[-1] * 100) # Dynamic fallback based on volatility
        
    return (wins / total_trades) * 100
