#!/usr/bin/env python3
"""
Multi-token comparison and correlation analysis.

Fetches data for multiple symbols and calculates price correlations.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from web3 import Web3
from eth_defi.gmx.config import GMXConfig
from eth_defi.gmx.ccxt import GMXCCXTWrapper
import pandas as pd
import numpy as np


def main():
    # Connect to Arbitrum
    web3 = Web3(Web3.HTTPProvider("https://arb1.arbitrum.io/rpc"))
    config = GMXConfig(web3)
    exchange = GMXCCXTWrapper(config)

    exchange.load_markets()

    symbols = ["ETH/USD", "BTC/USD", "ARB/USD"]
    timeframe = "1h"
    limit = 24

    print(f"Fetching hourly data for {len(symbols)} tokens...\n")

    # Collect data
    dfs = {}
    for symbol in symbols:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
            dfs[symbol] = df
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")

    # Display comparison
    print("Token Comparison (24h)")
    for symbol, df in dfs.items():
        if len(df) >= 2:
            first_price = df["close"].iloc[0]
            latest_price = df["close"].iloc[-1]
            change = latest_price - first_price
            change_pct = (change / first_price) * 100

            token = symbol.replace("/USD", "")
            print(f"{token:5} Current: ${latest_price:>10,.2f}  Change: {change:>+10,.2f} ({change_pct:>+6.2f}%)")

    # Calculate correlation matrix
    if len(dfs) >= 2:
        print("\nPrice Correlation Matrix")
        price_data = {}
        for symbol, df in dfs.items():
            token = symbol.replace("/USD", "")
            price_data[token] = df["close"].values

        tokens = list(price_data.keys())
        print(f"{'':5}", end="")
        for token in tokens:
            print(f"{token:>8}", end="")
        print()

        for token1 in tokens:
            print(f"{token1:5}", end="")
            for token2 in tokens:
                if token1 == token2:
                    corr = 1.00
                else:
                    corr = np.corrcoef(price_data[token1], price_data[token2])[0, 1]
                print(f"{corr:8.2f}", end="")
            print()


if __name__ == "__main__":
    main()
