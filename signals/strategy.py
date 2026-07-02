"""
Strategy signal generation: Buy and Sell rules.
"""

import pandas as pd

def buy_signal(df: pd.DataFrame, i: int) -> bool:
    """
    Check if a BUY signal occurs at candle index i (after close).

    Conditions:
    - Stochastic K[1] < 20 and K[0] > K[1]
    - ADX peaked: ADX[2] < ADX[1] and ADX[0] < ADX[1] and ADX[1] > 25
    - Heikin Ashi: both candle i-1 and i are bullish (HA_Bullish)

    Parameters
    ----------
    df : pd.DataFrame
        Data with required columns.
    i : int
        Index of the current candle (signal candle).

    Returns
    -------
    bool
    """
    if i < 2:  # need at least 3 candles
        return False

    # Stochastic condition (use index i-1 and i)
    k_prev = df["Stoch_K"].iloc[i-1]
    k_curr = df["Stoch_K"].iloc[i]
    if not (k_prev < 20 and k_curr > k_prev):
        return False

    # ADX condition (index i-2, i-1, i)
    adx_2 = df["ADX"].iloc[i-2]
    adx_1 = df["ADX"].iloc[i-1]
    adx_0 = df["ADX"].iloc[i]
    if not (adx_2 < adx_1 and adx_0 < adx_1 and adx_1 > 25):
        return False

    # Heikin Ashi condition
    ha_bull_prev = df["HA_Bullish"].iloc[i-1]
    ha_bull_curr = df["HA_Bullish"].iloc[i]
    if not (ha_bull_prev and ha_bull_curr):
        return False

    return True

def sell_signal(df: pd.DataFrame, i: int) -> bool:
    """
    Check if a SELL signal occurs at candle index i.

    Conditions:
    - Stochastic K[1] > 80 and K[0] < K[1]
    - ADX peaked: ADX[2] < ADX[1] and ADX[0] < ADX[1] and ADX[1] > 25
    - Heikin Ashi: both candle i-1 and i are bearish

    Parameters
    ----------
    df : pd.DataFrame
    i : int

    Returns
    -------
    bool
    """
    if i < 2:
        return False

    k_prev = df["Stoch_K"].iloc[i-1]
    k_curr = df["Stoch_K"].iloc[i]
    if not (k_prev > 80 and k_curr < k_prev):
        return False

    adx_2 = df["ADX"].iloc[i-2]
    adx_1 = df["ADX"].iloc[i-1]
    adx_0 = df["ADX"].iloc[i]
    if not (adx_2 < adx_1 and adx_0 < adx_1 and adx_1 > 25):
        return False

    ha_bear_prev = df["HA_Bearish"].iloc[i-1]
    ha_bear_curr = df["HA_Bearish"].iloc[i]
    if not (ha_bear_prev and ha_bear_curr):
        return False

    return True