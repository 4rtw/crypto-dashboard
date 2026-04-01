"""
Full-fidelity backtester — mirrors generate_signal_data() logic exactly.
Tests BUY/SELL signals with multiple exit strategies and produces
comprehensive performance metrics.

Usage:
    python backtest_full.py                        # BTC + ETH, 180 days, default exits
    python backtest_full.py --symbols BTCUSDT --days 365
    python backtest_full.py --tp 0.04 --sl 0.02   # fixed 4% TP / 2% SL
"""

import argparse
import json
import sys
import numpy as np
import pandas as pd
import pandas_ta as ta
from binance import Client
from logic import calculate_indicators, detect_rsi_divergence

# ─────────────────────────────────────────────────────────────────────────────
# Data fetching
# ─────────────────────────────────────────────────────────────────────────────

def fetch_klines(symbol: str, interval: str, days: int) -> pd.DataFrame:
    client = Client()
    raw = client.get_historical_klines(symbol, interval, f"{days} day ago UTC")
    df = pd.DataFrame(raw, columns=[
        "time", "open", "high", "low", "close", "volume",
        "close_time", "q_vol", "no_trades", "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    return df.reset_index(drop=True)


# ─────────────────────────────────────────────────────────────────────────────
# Full-fidelity signal replication (mirrors logic.py generate_signal_data)
# ─────────────────────────────────────────────────────────────────────────────

def get_signal_at(df_h1: pd.DataFrame, idx: int, df_h4: pd.DataFrame, h4_idx: int) -> str:
    """Return BUY / SELL / HOLD — mirrors logic.py generate_signal_data exactly."""
    if idx < 52:  # need enough bars for indicators + divergence lookback
        return "HOLD"

    window_h1 = df_h1.iloc[:idx + 1].copy()
    window_h4 = df_h4.iloc[:h4_idx + 1].copy() if h4_idx >= 1 else pd.DataFrame()

    last = window_h1.iloc[-1]
    prev = window_h1.iloc[-2]

    rsi       = last["rsi"]
    macd_line = last["MACD_12_26_9"]
    macd_sig  = last["MACDs_12_26_9"]
    volume    = last["volume"]
    vol_sma   = last["vol_sma"]

    # Improvement 1 — volume mandatory
    volume_ok = volume > vol_sma

    divergence = detect_rsi_divergence(window_h1)

    # Improvement 2 — H4 trend + RSI guard + macro regime (SMA50 vs SMA200)
    h4_trend     = "NEUTRAL"
    h4_rsi       = 50.0
    macro_regime = "NEUTRAL"
    if not window_h4.empty and len(window_h4) > 0:
        h4_last      = window_h4.iloc[-1]
        h4_trend     = "BULLISH" if h4_last["close"] > h4_last["sma_50"] else "BEARISH"
        h4_rsi       = float(h4_last["rsi"]) if not np.isnan(h4_last["rsi"]) else 50.0
        if "sma_200" in h4_last and not np.isnan(h4_last["sma_200"]):
            macro_regime = "BULL" if h4_last["sma_50"] > h4_last["sma_200"] else "BEAR"

    # Improvement 3 — 2-bar confirmation
    buy_confirmed  = prev["rsi"] < 45 and prev["MACD_12_26_9"] > prev["MACDs_12_26_9"]
    sell_confirmed = prev["rsi"] > 55 and prev["MACD_12_26_9"] < prev["MACDs_12_26_9"]

    # Improvement 4 — macro regime filter
    if rsi < 40 and macd_line > macd_sig and volume_ok and buy_confirmed:
        if divergence == "BULLISH" or h4_trend == "BULLISH":
            if h4_rsi < 65 and macro_regime != "BEAR":
                return "BUY"

    elif rsi > 60 and macd_line < macd_sig and volume_ok and sell_confirmed:
        if divergence == "BEARISH" or h4_trend == "BEARISH":
            if h4_rsi > 35 and macro_regime != "BULL":
                return "SELL"

    return "HOLD"


# ─────────────────────────────────────────────────────────────────────────────
# Backtest engine
# ─────────────────────────────────────────────────────────────────────────────

def backtest_symbol(
    symbol: str,
    days: int,
    tp: float,      # take-profit ratio  e.g. 0.03 = 3%
    sl: float,      # stop-loss ratio    e.g. 0.015 = 1.5%
    max_hold: int,  # max bars to hold before forced exit
) -> dict:
    print(f"  Fetching {days}d H1 data for {symbol}...", flush=True)
    df_h1 = fetch_klines(symbol, Client.KLINE_INTERVAL_1HOUR, days)
    print(f"  Fetching {days}d H4 data for {symbol}...", flush=True)
    df_h4 = fetch_klines(symbol, Client.KLINE_INTERVAL_4HOUR, days)

    # Pre-compute indicators once on full frame
    df_h1 = calculate_indicators(df_h1)
    df_h4 = calculate_indicators(df_h4)
    df_h1.dropna(inplace=True)
    df_h4.dropna(inplace=True)
    df_h1.reset_index(drop=True, inplace=True)
    df_h4.reset_index(drop=True, inplace=True)

    trades = []
    equity = [1.0]
    in_trade = False
    entry_price = 0.0
    entry_dir = None
    entry_bar = 0
    signal_count = {"BUY": 0, "SELL": 0, "HOLD": 0}

    for i in range(52, len(df_h1)):
        bar_time = df_h1.iloc[i]["time"]
        close    = df_h1.iloc[i]["close"]
        high     = df_h1.iloc[i]["high"]
        low      = df_h1.iloc[i]["low"]

        # Find corresponding H4 index (last H4 bar whose time <= H1 bar time)
        h4_idx = df_h4[df_h4["time"] <= bar_time].index
        h4_idx = int(h4_idx[-1]) if len(h4_idx) > 0 else 0

        if not in_trade:
            sig = get_signal_at(df_h1, i, df_h4, h4_idx)
            signal_count[sig] = signal_count.get(sig, 0) + 1

            if sig in ("BUY", "SELL"):
                in_trade   = True
                entry_price = close
                entry_dir  = sig
                entry_bar  = i
        else:
            bars_held = i - entry_bar
            pnl = 0.0
            exited = False

            if entry_dir == "BUY":
                # Check SL/TP on this bar (intrabar using high/low)
                if low <= entry_price * (1 - sl):
                    pnl = -sl
                    exited = True
                elif high >= entry_price * (1 + tp):
                    pnl = tp
                    exited = True
            else:  # SELL (short)
                if high >= entry_price * (1 + sl):
                    pnl = -sl
                    exited = True
                elif low <= entry_price * (1 - tp):
                    pnl = tp
                    exited = True

            # Force exit after max_hold bars at close price
            if not exited and bars_held >= max_hold:
                pnl = (close - entry_price) / entry_price
                if entry_dir == "SELL":
                    pnl = -pnl
                exited = True

            if exited:
                trades.append({
                    "entry_time":  df_h1.iloc[entry_bar]["time"],
                    "exit_time":   bar_time,
                    "direction":   entry_dir,
                    "entry_price": entry_price,
                    "exit_price":  close,
                    "pnl":         pnl,
                    "bars_held":   bars_held,
                })
                equity.append(equity[-1] * (1 + pnl))
                in_trade = False

    if not trades:
        return {
            "symbol":       symbol,
            "days":         days,
            "total_trades": 0,
            "note":         "No trades triggered — conditions too strict for this period",
        }

    pnls   = np.array([t["pnl"] for t in trades])
    wins   = pnls[pnls > 0]
    losses = pnls[pnls <= 0]

    # Max drawdown on equity curve
    eq = np.array(equity)
    peak = np.maximum.accumulate(eq)
    dd   = (eq - peak) / peak
    max_dd = float(dd.min() * 100)

    # Sharpe (annualised, assumes 1h bars ≈ 8760 bars/year)
    mean_pnl = pnls.mean()
    std_pnl  = pnls.std() if pnls.std() > 0 else 1e-9
    bars_per_year = 365 * 24
    avg_bars_held = float(np.mean([t["bars_held"] for t in trades]))
    trades_per_year = bars_per_year / max(avg_bars_held, 1)
    sharpe = float((mean_pnl / std_pnl) * np.sqrt(trades_per_year))

    # Profit factor
    gross_win  = float(wins.sum())  if len(wins)   > 0 else 0
    gross_loss = float(abs(losses.sum())) if len(losses) > 0 else 1e-9
    profit_factor = gross_win / gross_loss

    # Consecutive stats
    streaks = []
    current = 0
    for p in pnls:
        if p > 0:
            current = current + 1 if current > 0 else 1
        else:
            current = current - 1 if current < 0 else -1
        streaks.append(current)
    max_win_streak  = max((s for s in streaks if s > 0), default=0)
    max_loss_streak = abs(min((s for s in streaks if s < 0), default=0))

    return {
        "symbol":           symbol,
        "days":             days,
        "params":           {"tp_pct": tp * 100, "sl_pct": sl * 100, "max_hold_bars": max_hold},
        "signal_counts":    signal_count,
        "total_trades":     len(trades),
        "wins":             int(len(wins)),
        "losses":           int(len(losses)),
        "winrate_pct":      round(len(wins) / len(trades) * 100, 2),
        "avg_win_pct":      round(float(wins.mean() * 100),   2) if len(wins)   > 0 else 0,
        "avg_loss_pct":     round(float(losses.mean() * 100), 2) if len(losses) > 0 else 0,
        "avg_trade_pct":    round(float(pnls.mean() * 100),   2),
        "best_trade_pct":   round(float(pnls.max() * 100),    2),
        "worst_trade_pct":  round(float(pnls.min() * 100),    2),
        "profit_factor":    round(profit_factor, 2),
        "total_return_pct": round((equity[-1] - 1) * 100,     2),
        "max_drawdown_pct": round(max_dd, 2),
        "sharpe_ratio":     round(sharpe, 2),
        "avg_hold_bars":    round(avg_bars_held, 1),
        "max_win_streak":   max_win_streak,
        "max_loss_streak":  max_loss_streak,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Pretty print
# ─────────────────────────────────────────────────────────────────────────────

def print_results(results: list[dict]):
    SEP = "─" * 60
    for r in results:
        print(f"\n{SEP}")
        print(f"  {r['symbol']}  —  {r['days']}d backtest")
        print(SEP)

        if "note" in r:
            print(f"  {r['note']}")
            continue

        p = r["params"]
        print(f"  Params : TP {p['tp_pct']}%  SL {p['sl_pct']}%  MaxHold {p['max_hold_bars']}h")
        print(f"  Signals: {r['signal_counts']}")
        print()
        print(f"  Trades        : {r['total_trades']}  ({r['wins']}W / {r['losses']}L)")
        print(f"  Winrate       : {r['winrate_pct']}%")
        print(f"  Avg trade     : {r['avg_trade_pct']}%")
        print(f"  Avg win / loss: {r['avg_win_pct']}% / {r['avg_loss_pct']}%")
        print(f"  Best / Worst  : {r['best_trade_pct']}% / {r['worst_trade_pct']}%")
        print(f"  Profit factor : {r['profit_factor']}")
        print(f"  Total return  : {r['total_return_pct']}%")
        print(f"  Max drawdown  : {r['max_drawdown_pct']}%")
        print(f"  Sharpe ratio  : {r['sharpe_ratio']}")
        print(f"  Avg hold      : {r['avg_hold_bars']}h")
        print(f"  Streaks W/L   : {r['max_win_streak']} / {r['max_loss_streak']}")
    print(f"\n{SEP}\n")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Full-fidelity signal backtester")
    parser.add_argument("--symbols",  nargs="+", default=["BTCUSDT", "ETHUSDT"])
    parser.add_argument("--days",     type=int,   default=180,  help="History window in days")
    parser.add_argument("--tp",       type=float, default=0.03, help="Take-profit ratio (0.03 = 3%%)")
    parser.add_argument("--sl",       type=float, default=0.015, help="Stop-loss ratio (0.015 = 1.5%%)")
    parser.add_argument("--max-hold", type=int,   default=48,   help="Max bars to hold before forced exit")
    parser.add_argument("--json",     action="store_true",      help="Output raw JSON instead of table")
    args = parser.parse_args()

    all_results = []
    for sym in args.symbols:
        try:
            res = backtest_symbol(
                symbol=sym,
                days=args.days,
                tp=args.tp,
                sl=args.sl,
                max_hold=args.max_hold,
            )
            all_results.append(res)
        except Exception as e:
            all_results.append({"symbol": sym, "error": str(e)})
            print(f"  ERROR {sym}: {e}", file=sys.stderr)

    if args.json:
        print(json.dumps(all_results, indent=2, default=str))
    else:
        print_results(all_results)
