"""
Performance analytics for backtest results.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple

def compute_metrics(trades: pd.DataFrame, initial_balance: float = 10000.0) -> dict:
    """
    Calculate key performance statistics.

    Parameters
    ----------
    trades : pd.DataFrame
        Must contain 'r_multiple' and 'entry_time'.
    initial_balance : float

    Returns
    -------
    dict with metrics.
    """
    if trades.empty:
        return {"total_trades": 0}

    total = len(trades)
    wins = (trades["result"] == "WIN").sum()
    losses = (trades["result"] == "LOSS").sum()
    win_rate = wins / total if total > 0 else 0.0
    avg_r = trades["r_multiple"].mean()
    net_r = trades["r_multiple"].sum()
    profit_factor = abs(trades[trades["r_multiple"] > 0]["r_multiple"].sum() / 
                         trades[trades["r_multiple"] < 0]["r_multiple"].sum()) if losses > 0 else np.inf
    expectancy = avg_r

    # Equity curve
    equity = initial_balance + (initial_balance * 0.01) * trades["r_multiple"].cumsum()
    equity = pd.Series(equity.values, index=trades["entry_time"])

    # Drawdown
    rolling_max = equity.cummax()
    drawdown = (equity - rolling_max) / rolling_max
    max_drawdown = drawdown.min()

    # Longest losing streak
    streak = (trades["result"] == "LOSS").astype(int)
    losing_streak = streak.groupby((streak != streak.shift()).cumsum()).cumsum().max()

    # Average trade duration (hours)
    durations = (trades["exit_time"] - trades["entry_time"]).dt.total_seconds() / 3600
    avg_duration = durations.mean()

    # Monthly returns
    monthly_equity = equity.resample("ME").last()
    monthly_returns = monthly_equity.pct_change().dropna()

    return {
        "total_trades": total,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "average_r": avg_r,
        "net_r": net_r,
        "profit_factor": profit_factor,
        "expectancy": expectancy,
        "max_drawdown": max_drawdown,
        "longest_losing_streak": losing_streak,
        "avg_trade_duration_hours": avg_duration,
        "monthly_returns": monthly_returns,
        "equity_curve": equity,
        "drawdown_curve": drawdown
    }

def plot_equity_curve(equity: pd.Series, drawdown: pd.Series):
    """Simple equity and drawdown plot."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    ax1.plot(equity.index, equity.values, label="Equity")
    ax1.set_title("Equity Curve")
    ax1.legend()

    ax2.fill_between(drawdown.index, drawdown.values * 100, 0, color="red", alpha=0.3)
    ax2.set_title("Drawdown %")
    ax2.set_xlabel("Date")
    plt.tight_layout()
    plt.show()