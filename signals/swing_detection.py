"""
Swing Highs and Lows detection.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional

def detect_swings(df: pd.DataFrame, lookback: int = 3) -> pd.DataFrame:
    """
    Mark swing highs and lows.

    A swing high occurs when High[i] is greater than the previous `lookback` highs.
    A swing low occurs when Low[i] is lower than the previous `lookback` lows.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain 'high' and 'low'.
    lookback : int
        Number of candles to the left to compare (default 3).

    Returns
    -------
    pd.DataFrame
        DataFrame with Boolean columns 'SwingHigh' and 'SwingLow'.
    """
    df["SwingHigh"] = False
    df["SwingLow"] = False

    for i in range(lookback, len(df)):
        # Check swing high: high[i] > all previous lookback highs
        if all(df["high"].iloc[i] > df["high"].iloc[i-j] for j in range(1, lookback+1)):
            df.at[df.index[i], "SwingHigh"] = True

        # Check swing low
        if all(df["low"].iloc[i] < df["low"].iloc[i-j] for j in range(1, lookback+1)):
            df.at[df.index[i], "SwingLow"] = True

    return df

def last_swing_high(df: pd.DataFrame, before_index: int) -> Optional[float]:
    """
    Get the most recent swing high price strictly before a given index.

    Parameters
    ----------
    df : pd.DataFrame
        Data with 'SwingHigh' column.
    before_index : int
        Index of the current candle (entry signal is after this).

    Returns
    -------
    float or None
        The high price of the last swing high, or None if not found.
    """
    mask = (df["SwingHigh"]) & (df.index < df.index[before_index])
    if mask.any():
        return df.loc[mask, "high"].iloc[-1]
    return None

def last_swing_low(df: pd.DataFrame, before_index: int) -> Optional[float]:
    """
    Get the most recent swing low price strictly before a given index.

    Parameters
    ----------
    df : pd.DataFrame
        Data with 'SwingLow' column.
    before_index : int
        Index of the current candle.

    Returns
    -------
    float or None
        The low price of the last swing low, or None.
    """
    mask = (df["SwingLow"]) & (df.index < df.index[before_index])
    if mask.any():
        return df.loc[mask, "low"].iloc[-1]
    return None