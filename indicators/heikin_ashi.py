"""
Heikin-Ashi candle calculations.
"""

import pandas as pd

def calculate_heikin_ashi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Heikin-Ashi OHLC and add bullish/bearish columns.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain 'open', 'high', 'low', 'close'.

    Returns
    -------
    pd.DataFrame
        DataFrame with added columns: HA_Open, HA_High, HA_Low, HA_Close,
        HA_Bullish, HA_Bearish.
    """
    ha = pd.DataFrame(index=df.index)
    ha["HA_Close"] = (df["open"] + df["high"] + df["low"] + df["close"]) / 4.0

    # First HA_Open = (Open + Close) / 2
    ha_open = (df["open"].iloc[0] + df["close"].iloc[0]) / 2.0
    ha_open_list = [ha_open]

    for i in range(1, len(df)):
        ha_open = (ha_open_list[-1] + ha["HA_Close"].iloc[i-1]) / 2.0
        ha_open_list.append(ha_open)

    ha["HA_Open"] = ha_open_list
    ha["HA_High"] = df[["high", "low"]].join(ha[["HA_Open", "HA_Close"]]).max(axis=1)
    ha["HA_Low"] = df[["high", "low"]].join(ha[["HA_Open", "HA_Close"]]).min(axis=1)

    ha["HA_Bullish"] = ha["HA_Close"] > ha["HA_Open"]
    ha["HA_Bearish"] = ha["HA_Close"] < ha["HA_Open"]

    # Add HA columns to original df (keep originals)
    for col in ha.columns:
        df[col] = ha[col]

    return df