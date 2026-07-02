"""
Swing Highs and Lows detection with minimum distance constraint.
"""

import pandas as pd
from typing import Optional

def detect_swings(df: pd.DataFrame, lookback: int = 3, min_distance: int = 5) -> pd.DataFrame:
    """
    Mark swing highs and lows.

    A swing high occurs when High[i] > previous `lookback` highs.
    A swing low occurs when Low[i] < previous `lookback` lows.
    Additionally, consecutive same-type swings must be separated by at least
    `min_distance` bars.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain 'high' and 'low'.
    lookback : int
        Number of candles to the left to compare (default 3).
    min_distance : int
        Minimum number of bars between two swing highs (or two swing lows).

    Returns
    -------
    pd.DataFrame
        DataFrame with Boolean columns 'SwingHigh' and 'SwingLow'.
    """
    df["SwingHigh"] = False
    df["SwingLow"] = False

    last_high_idx = -min_distance - 1
    last_low_idx = -min_distance - 1

    for i in range(lookback, len(df)):
        # Swing high check
        if all(df["high"].iloc[i] > df["high"].iloc[i-j] for j in range(1, lookback+1)):
            if i - last_high_idx >= min_distance:
                df.at[df.index[i], "SwingHigh"] = True
                last_high_idx = i

        # Swing low check
        if all(df["low"].iloc[i] < df["low"].iloc[i-j] for j in range(1, lookback+1)):
            if i - last_low_idx >= min_distance:
                df.at[df.index[i], "SwingLow"] = True
                last_low_idx = i

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