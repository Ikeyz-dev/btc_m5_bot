"""
Risk management: position sizing, stop loss, take profit.
"""

from typing import Optional, Tuple
import pandas as pd
from signals.swing_detection import last_swing_high, last_swing_low

def calculate_stop_loss(
    df: pd.DataFrame,
    signal_index: int,
    trade_type: str,
    atr_multiplier: float = 0.2
) -> Optional[float]:
    """
    Compute stop loss price based on swing point and ATR.

    Parameters
    ----------
    df : pd.DataFrame
    signal_index : int
        Index of the signal candle.
    trade_type : str
        'BUY' or 'SELL'.
    atr_multiplier : float
        Fraction of ATR to add/subtract.

    Returns
    -------
    float or None
        Stop loss price.
    """
    atr = df["ATR"].iloc[signal_index]
    if trade_type == "BUY":
        swing_low = last_swing_low(df, signal_index + 1)  # entry is next candle
        if swing_low is None:
            return None
        return swing_low - atr_multiplier * atr
    else:  # SELL
        swing_high = last_swing_high(df, signal_index + 1)
        if swing_high is None:
            return None
        return swing_high + atr_multiplier * atr

def calculate_take_profit(
    entry_price: float,
    stop_loss: float,
    trade_type: str,
    risk_reward: float = 2.0
) -> float:
    """
    Fixed risk-reward take profit.

    For BUY: TP = entry + RR * (entry - SL)
    For SELL: TP = entry - RR * (SL - entry)

    Parameters
    ----------
    entry_price : float
    stop_loss : float
    trade_type : str
    risk_reward : float

    Returns
    -------
    float
    """
    if trade_type == "BUY":
        risk = entry_price - stop_loss
        return entry_price + risk_reward * risk
    else:
        risk = stop_loss - entry_price
        return entry_price - risk_reward * risk

def position_size(
    account_balance: float,
    risk_per_trade: float,
    entry_price: float,
    stop_loss: float
) -> float:
    """
    Calculate position size (in base currency) risking `risk_per_trade` fraction.

    Parameters
    ----------
    account_balance : float
    risk_per_trade : float
        e.g., 0.01 for 1%.
    entry_price : float
    stop_loss : float

    Returns
    -------
    float
        Amount of BTC to buy/sell.
    """
    risk_amount = account_balance * risk_per_trade
    stop_distance = abs(entry_price - stop_loss)
    if stop_distance == 0:
        return 0.0
    return risk_amount / stop_distance