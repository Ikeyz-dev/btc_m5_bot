"""
ATR calculation.
"""

import pandas as pd
from ta.volatility import AverageTrueRange

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Compute Average True Range.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain 'high', 'low', 'close'.
    period : int
        ATR period (default 14).

    Returns
    -------
    pd.DataFrame
        DataFrame with added column 'ATR'.
    """
    atr_indicator = AverageTrueRange(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        window=period
    )
    df["ATR"] = atr_indicator.average_true_range().round(2)
    return df