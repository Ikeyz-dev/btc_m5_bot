"""
Data loading module using CCXT.
Downloads BTC/USDT 5-minute OHLCV from Binance.
"""

from datetime import datetime
from typing import Optional
import pandas as pd
import ccxt

def download_data(
    symbol: str = "BTC/USDT",
    timeframe: str = "5m",
    limit: Optional[int] = 1000,
    since: Optional[int] = None
) -> pd.DataFrame:
    """
    Download historical OHLCV data from Binance.

    Parameters
    ----------
    symbol : str
        Trading pair (default 'BTC/USDT').
    timeframe : str
        Candle timeframe (default '5m').
    limit : int, optional
        Number of candles to fetch per request.
    since : int, optional
        Timestamp in milliseconds for the start of data.

    Returns
    -------
    pd.DataFrame
        Columns: timestamp, open, high, low, close, volume.
        Timestamp set as index.
    """
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit, since=since)
    df = pd.DataFrame(
        ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df.sort_index(inplace=True)
    return df