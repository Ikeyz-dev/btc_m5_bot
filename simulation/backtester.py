"""
Backtester: scans candles, generates signals, manages trades.
"""

import pandas as pd
from typing import List, Optional
from signals.strategy import buy_signal, sell_signal
from signals.swing_detection import detect_swings
from risk.manager import calculate_stop_loss, calculate_take_profit
from simulation.trade_simulator import simulate_trade


def backtest(
    df: pd.DataFrame,
    initial_balance: float = 10000.0,
    risk_per_trade: float = 0.01,
    max_daily_losses: int = 3,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Run backtest on prepared DataFrame with all indicators.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain OHLC, HA, Stoch_K, ADX, ATR, SwingHigh/Low, and optionally EMA_200.
    initial_balance : float
    risk_per_trade : float
    max_daily_losses : int
        Max losing trades allowed per calendar day.
    verbose : bool
        Print detailed signal information.

    Returns
    -------
    pd.DataFrame
        All completed trades with columns:
        entry_time, exit_time, type, entry_price, stop_loss, take_profit,
        exit_price, result, r_multiple, exit_reason, duration_hours
    """
    trades = []
    balance = initial_balance
    in_trade = False
    i = 3  # start after enough candles for indicators

    daily_loss_count = {}
    current_trade_day = None

    while i < len(df) - 1:  # need next candle for entry
        if in_trade:
            i += 1
            continue

        signal_day = df.index[i].date()

        # Reset daily loss counter if new day
        if current_trade_day != signal_day:
            current_trade_day = signal_day
            daily_loss_count[current_trade_day] = 0

        # Check daily loss limit
        if daily_loss_count.get(current_trade_day, 0) >= max_daily_losses:
            i += 1
            continue

        # Check signals
        trade_type = None
        if buy_signal(df, i):
            trade_type = "BUY"
        elif sell_signal(df, i):
            trade_type = "SELL"

        if trade_type is None:
            i += 1
            continue

        # Entry price is open of next candle
        entry_index = i + 1
        if entry_index >= len(df):
            break
        entry_price = df["open"].iloc[entry_index]

        # Stop loss (uses updated defaults: atr_multiplier=0.5, min_stop_pct=0.005)
        stop_loss = calculate_stop_loss(df, i, trade_type)
        if stop_loss is None:
            i += 1
            continue

        # Take profit (fixed 2R)
        take_profit = calculate_take_profit(entry_price, stop_loss, trade_type, risk_reward=2.0)

        if verbose:
            print(f"Signal at {df.index[i]} | Type: {trade_type} | "
                  f"Price: {df['close'].iloc[i]:.2f} | "
                  f"K: {df['Stoch_K'].iloc[i-1]:.2f}->{df['Stoch_K'].iloc[i]:.2f} | "
                  f"ADX peak: {df['ADX'].iloc[i-1]:.2f} | "
                  f"SL: {stop_loss:.2f} | TP: {take_profit:.2f}")

        # Simulate trade
        result = simulate_trade(df, entry_index, entry_price, stop_loss, take_profit, trade_type)
        if result is None:
            # Trade never exited – skip
            i = entry_index + 1
            continue

        # Calculate duration
        duration_hours = (result["exit_time"] - df.index[entry_index]).total_seconds() / 3600

        # Record trade
        trade_record = {
            "entry_time": df.index[entry_index],
            "exit_time": result["exit_time"],
            "type": trade_type,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "exit_price": result["exit_price"],
            "result": result["result"],
            "r_multiple": result["r_multiple"],
            "exit_reason": "SL" if result["result"] == "LOSS" else "TP",
            "duration_hours": round(duration_hours, 2)
        }
        trades.append(trade_record)

        # Update balance (R-multiple)
        risk_amount = balance * risk_per_trade
        balance += risk_amount * result["r_multiple"]

        # Update daily loss count
        if result["result"] == "LOSS":
            daily_loss_count[current_trade_day] = daily_loss_count.get(current_trade_day, 0) + 1

        # Move index past trade exit
        i = result["exit_index"] + 1  # next candle after exit

    return pd.DataFrame(trades)