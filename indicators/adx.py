"""
ADX calculation.
"""

import pandas as pd
from ta.trend import ADXIndicator

def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Compute ADX (Average Directional Index).

    Parameters
    ----------
    df : pd.DataFrame
        Must contain 'high', 'low', 'close'.
    period : int
        ADX period (default 14).

    Returns
    -------
    pd.DataFrame
        DataFrame with added column 'ADX'.
    """
    adx_indicator = ADXIndicator(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        window=period
    )
    df["ADX"] = adx_indicator.adx().round(2)
    return df