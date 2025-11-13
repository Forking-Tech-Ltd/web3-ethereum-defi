#!/usr/bin/env python3
"""
Basic OHLCV data fetching example.

Demonstrates fetching candlestick data from GMX using CCXT-compatible interface.
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

    # Load markets
    print("Loading markets...")
    markets = exchange.load_markets()
    print(f"Loaded {len(markets)} markets")

    # Fetch OHLCV data
    symbol = "ETH/USD"
    timeframe = "1h"
    limit = 50

    print(f"\nFetching {symbol} {timeframe} candles (last {limit})...")
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

    # Convert to DataFrame
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

    # Calculate statistics
    print(f"\nReceived {len(ohlcv)} candles")
    print(f"Latest price: ${df['close'].iloc[-1]:,.2f}")
    print(f"24h High: ${df['high'].tail(24).max():,.2f}")
    print(f"24h Low: ${df['low'].tail(24).min():,.2f}")

    # Display recent candles
    print("\nRecent candles (last 5):")
    print(df[["timestamp", "open", "high", "low", "close"]].tail(5).to_string(index=False))


if __name__ == "__main__":
    main()
