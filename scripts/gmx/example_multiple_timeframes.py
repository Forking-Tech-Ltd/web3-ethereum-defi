#!/usr/bin/env python3
"""
Multiple timeframes analysis example.

Fetches and compares OHLCV data across different timeframes.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from web3 import Web3
from eth_defi.gmx.config import GMXConfig
from eth_defi.gmx.ccxt import GMXCCXTWrapper
import pandas as pd


def main():
    # Connect to Arbitrum
    web3 = Web3(Web3.HTTPProvider("https://arb1.arbitrum.io/rpc"))
    config = GMXConfig(web3)
    exchange = GMXCCXTWrapper(config)

    exchange.load_markets()

    symbol = "BTC/USD"
    timeframes = ["1m", "15m", "1h", "1d"]

    print(f"Fetching {symbol} data for multiple timeframes...\n")

    results = []
    for tf in timeframes:
        ohlcv = exchange.fetch_ohlcv(symbol, tf, limit=10)
        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])

        first_price = df["open"].iloc[0]
        last_price = df["close"].iloc[-1]
        change_pct = ((last_price - first_price) / first_price) * 100

        results.append({
            "Timeframe": tf,
            "Latest Price": f"${last_price:,.2f}",
            "Change %": f"{change_pct:+.2f}%",
            "High": f"${df['high'].max():,.2f}",
            "Low": f"${df['low'].min():,.2f}"
        })

    # Display results
    result_df = pd.DataFrame(results)
    print(result_df.to_string(index=False))


if __name__ == "__main__":
    main()
