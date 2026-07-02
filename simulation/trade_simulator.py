"""
Single trade simulation: walk forward through candles.
Implements conservative SL-first assumption.
"""

from typing import Optional, Tuple, Dict, Any
import pandas as pd

def simulate_trade(
    df: pd.DataFrame,
    entry_index: int,
    entry_price: float,
    stop_loss: float,
    take_profit: float,
    trade_type: str
) -> Dict[str, Any]:
    """
    Simulate a trade from entry_index to exit.

    Scans forward candle by candle. If both SL and TP are touched in
    the same candle, stop loss is assumed hit first.

    Parameters
    ----------
    df : pd.DataFrame
        Full OHLC data (will be sliced from entry_index onward).
    entry_index : int
        Index of the entry candle (the candle where we enter on open).
    entry_price : float
    stop_loss : float
    take_profit : float
    trade_type : str
        'BUY' or 'SELL'.

    Returns
    -------
    dict with keys:
        exit_price, exit_time, result (WIN/LOSS), r_multiple, exit_index
        Returns None if trade never exits (open at end of data).
    """
    # Slice from entry candle forward
    trade_df = df.iloc[entry_index:]
    if len(trade_df) == 0:
        return None

    for idx, (i, row) in enumerate(trade_df.iterrows()):
        if trade_type == "BUY":
            # Check stop loss first
            if row["low"] <= stop_loss:
                return {
                    "exit_price": stop_loss,
                    "exit_time": i,
                    "result": "LOSS",
                    "r_multiple": -1.0,
                    "exit_index": entry_index + idx
                }
            # Check take profit
            if row["high"] >= take_profit:
                return {
                    "exit_price": take_profit,
                    "exit_time": i,
                    "result": "WIN",
                    "r_multiple": 2.0,
                    "exit_index": entry_index + idx
                }
        else:  # SELL
            # Check stop loss first
            if row["high"] >= stop_loss:
                return {
                    "exit_price": stop_loss,
                    "exit_time": i,
                    "result": "LOSS",
                    "r_multiple": -1.0,
                    "exit_index": entry_index + idx
                }
            # Check take profit
            if row["low"] <= take_profit:
                return {
                    "exit_price": take_profit,
                    "exit_time": i,
                    "result": "WIN",
                    "r_multiple": 2.0,
                    "exit_index": entry_index + idx
                }

    # If loop finishes without exit
    return None