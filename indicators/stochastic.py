"""
Stochastic Oscillator calculation.
Uses ta library.
"""

import pandas as pd
from ta.momentum import StochasticOscillator

def calculate_stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3, slowing: int = 3):
    """
    Compute Stochastic %K and %D.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain 'high', 'low', 'close'.
    k_period : int
        %K period (default 14).
    d_period : int
        %D period (default 3).
    slowing : int
        Slowing period (default 3).

    Returns
    -------
    pd.DataFrame
        DataFrame with added columns 'Stoch_K' and 'Stoch_D'.
        Note: %K is the 'slow' stochastic (already smoothed).
    """
    stoch = StochasticOscillator(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        window=k_period,
        smooth_window=slowing
    )
    df["Stoch_K"] = stoch.stoch().round(2)
    df["Stoch_D"] = stoch.stoch_signal().round(2)
    return df