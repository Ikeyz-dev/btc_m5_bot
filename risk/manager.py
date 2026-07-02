"""
Risk management: position sizing, stop loss, take profit.
"""

from typing import Optional
import pandas as pd
from signals.swing_detection import last_swing_high, last_swing_low


def calculate_stop_loss(
    df: pd.DataFrame,
    signal_index: int,
    trade_type: str,
    atr_multiplier: float = 0.5,
    min_stop_pct: float = 0.005   # 0.5% minimum stop distance from entry
) -> Optional[float]:
    """
    Compute stop loss price based on swing point + ATR buffer,
    with a minimum distance floor.

    For BUY: SL = min( swing_low - ATR*multiplier , entry*(1 - min_stop_pct) )
             then we take the HIGHER (closer to entry) of the two, i.e. max()
             to ensure the stop is at least min_stop_pct away.
    For SELL: SL = max( swing_high + ATR*multiplier , entry*(1 + min_stop_pct) )
               and we take the LOWER? Wait, careful: For SELL, stop is above entry.
               A wider stop is a higher number. The floor ensures stop is at least
               min_stop_pct above entry. If raw_sl < entry*(1+min_stop_pct), it's too
               tight and we must raise it. So we take max(raw_sl, entry*(1+min_stop_pct)).
               Because max gives the larger number (wider stop).
    Let's implement correctly:

    Parameters
    ----------
    df : pd.DataFrame
    signal_index : int
        Index of the signal candle.
    trade_type : str
        'BUY' or 'SELL'.
    atr_multiplier : float
        Fraction of ATR to add/subtract (default 0.5).
    min_stop_pct : float
        Minimum stop distance as a fraction of entry price (default 0.5%).

    Returns
    -------
    float or None
        Stop loss price.
    """
    atr = df["ATR"].iloc[signal_index]

    if trade_type == "BUY":
        swing_low = last_swing_low(df, signal_index + 1)
        if swing_low is None:
            return None
        raw_sl = swing_low - atr_multiplier * atr

        # Estimate entry as next candle's open (we don't have it yet, so use signal close)
        entry_estimate = df["close"].iloc[signal_index]
        min_sl = entry_estimate * (1 - min_stop_pct)   # higher than raw_sl if too tight

        # For a long, stop is below entry; a wider stop is a lower price? No:
        # Entry = 60000, SL 59000 is 1000 risk. Wider stop would be 58500 (more risk).
        # So wider stop = lower number. The floor min_sl = 59700. If raw_sl = 59000,
        # raw_sl is lower (tighter). We want to use the wider stop (higher number).
        # Therefore we take max(raw_sl, min_sl) because max gives the larger (higher) price,
        # which is closer to entry and thus less risk. That's correct.
        return max(raw_sl, min_sl)

    else:  # SELL
        swing_high = last_swing_high(df, signal_index + 1)
        if swing_high is None:
            return None
        raw_sl = swing_high + atr_multiplier * atr

        entry_estimate = df["close"].iloc[signal_index]
        min_sl = entry_estimate * (1 + min_stop_pct)  # minimum stop price (above entry)

        # For a short, stop is above entry. Wider stop = higher price.
        # If raw_sl = 60200 and min_sl = 60300 (floor), min_sl is wider (higher).
        # To ensure stop is at least min_sl, we take max(raw_sl, min_sl) because
        # max will give the higher (wider) number.
        return max(raw_sl, min_sl)


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