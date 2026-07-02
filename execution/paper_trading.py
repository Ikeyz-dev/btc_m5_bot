"""
Paper trading implementation using a live data feed.
Prints signals but does not place real orders.
"""

import time
import pandas as pd
from datetime import datetime, timedelta
from data.data_loader import download_data
from signals.strategy import buy_signal, sell_signal
from risk.manager import calculate_stop_loss, calculate_take_profit, position_size

def run_live(risk_per_trade: float = 0.01, balance: float = 10000.0):
    """
    Paper trading loop: fetch latest 5m candle, evaluate strategy, print signals.
    """
    print("Paper trading started...")
    # Initialize historical data (at least 100 candles)
    df = download_data(symbol="BTC/USDT", timeframe="5m", limit=100)
    # Compute all indicators (code omitted for brevity – call all indicator functions)
    # We'll assume df already has all columns (in real code you'd recompute on each step)

    while True:
        # Wait until next 5-minute candle
        now = datetime.utcnow()
        next_candle = now + timedelta(minutes=5 - now.minute % 5, seconds=-now.second)
        sleep_seconds = (next_candle - now).total_seconds()
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

        # Fetch latest candle
        new_data = download_data(symbol="BTC/USDT", timeframe="5m", limit=1)
        df = pd.concat([df, new_data]).iloc[-200:]  # keep last 200 rows

        # Recalculate indicators on the full df (for simplicity)
        from indicators.heikin_ashi import calculate_heikin_ashi
        from indicators.stochastic import calculate_stochastic
        from indicators.adx import calculate_adx
        from indicators.atr import calculate_atr
        from signals.swing_detection import detect_swings

        calculate_heikin_ashi(df)
        calculate_stochastic(df)
        calculate_adx(df)
        calculate_atr(df)
        detect_swings(df)

        # Last closed candle is index -1
        i = len(df) - 1
        if buy_signal(df, i):
            entry = df["open"].iloc[-1]  # next candle's open approx (we'll use last close for demo)
            sl = calculate_stop_loss(df, i, "BUY")
            tp = calculate_take_profit(entry, sl, "BUY")
            size = position_size(balance, risk_per_trade, entry, sl)
            print(f"BUY SIGNAL | Entry: {entry:.2f} | SL: {sl:.2f} | TP: {tp:.2f} | Size: {size:.4f} BTC")
        elif sell_signal(df, i):
            entry = df["open"].iloc[-1]
            sl = calculate_stop_loss(df, i, "SELL")
            tp = calculate_take_profit(entry, sl, "SELL")
            size = position_size(balance, risk_per_trade, entry, sl)
            print(f"SELL SIGNAL | Entry: {entry:.2f} | SL: {sl:.2f} | TP: {tp:.2f} | Size: {size:.4f} BTC")
        else:
            print("NO SIGNAL")