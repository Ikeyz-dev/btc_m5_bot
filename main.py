"""
Main entry point: download data, compute indicators, backtest, show results.
"""

import pandas as pd
from data.data_loader import download_data
from indicators.heikin_ashi import calculate_heikin_ashi
from indicators.stochastic import calculate_stochastic
from indicators.adx import calculate_adx
from indicators.atr import calculate_atr
from signals.swing_detection import detect_swings
from simulation.backtester import backtest
from analytics.performance import compute_metrics, plot_equity_curve
import config

def main():
    # Download 5000 5-min candles (~17 days)
    print("Downloading data...")
    df = download_data(limit=5000)

    # Compute all indicators
    print("Computing Heikin Ashi...")
    df = calculate_heikin_ashi(df)
    print("Stochastic...")
    df = calculate_stochastic(df, config.STOCH_K, config.STOCH_D, config.STOCH_SLOWING)
    print("ADX...")
    df = calculate_adx(df, config.ADX_PERIOD)
    print("ATR...")
    df = calculate_atr(df, config.ATR_PERIOD)
    print("Swing detection...")
    df = detect_swings(df, config.SWING_LOOKBACK)

    # Drop NaN rows caused by indicator lookback
    df.dropna(inplace=True)

    # Run backtest
    print("Running backtest...")
    trades = backtest(df, initial_balance=10000, risk_per_trade=config.RISK_PER_TRADE,
                      max_daily_losses=config.MAX_DAILY_LOSSES)

    if trades.empty:
        print("No trades generated.")
        return

    # Performance metrics
    metrics = compute_metrics(trades, initial_balance=10000)
    print("\n--- Backtest Results ---")
    for k, v in metrics.items():
        if k not in ("monthly_returns", "equity_curve", "drawdown_curve"):
            print(f"{k}: {v}")

    # Plot equity and drawdown
    plot_equity_curve(metrics["equity_curve"], metrics["drawdown_curve"])

    # Save trades to CSV
    trades.to_csv("trades_log.csv", index=False)
    print("\nTrades saved to trades_log.csv")

if __name__ == "__main__":
    main()