#!/usr/bin/env python3
"""
Historical data fetching example using the 'since' parameter.

Demonstrates fetching data from a specific timestamp and calculating performance metrics.
"""

import sys
from pathlib import Path
import time

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

    symbol = "ETH/USD"
    timeframe = "1h"

    # Fetch data from 24 hours ago
    since = int((time.time() - 86400) * 1000)

    print(f"Fetching {symbol} {timeframe} candles from last 24 hours...\n")
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=24)

    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

    # Calculate performance metrics
    first_price = df["close"].iloc[0]
    last_price = df["close"].iloc[-1]
    price_change = last_price - first_price
    price_change_pct = (price_change / first_price) * 100

    max_price = df["high"].max()
    min_price = df["low"].min()
    avg_price = df["close"].mean()
    std_dev = df["close"].std()

    print(f"24-Hour Performance for {symbol}")
    print(f"Start Price: ${first_price:,.2f}")
    print(f"End Price: ${last_price:,.2f}")
    print(f"Change: ${price_change:+,.2f} ({price_change_pct:+.2f}%)")
    print(f"\n24h High: ${max_price:,.2f}")
    print(f"24h Low: ${min_price:,.2f}")
    print(f"Average: ${avg_price:,.2f}")
    print(f"Std Dev: ${std_dev:.2f}")
    print(f"Volatility: {(std_dev / avg_price * 100):.2f}%")


if __name__ == "__main__":
    main()
