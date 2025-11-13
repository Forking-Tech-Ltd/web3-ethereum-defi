#!/usr/bin/env python3
"""
GMX CCXT Interface Example

This script demonstrates how to use the CCXT-compatible interface for GMX protocol.
It shows how to fetch OHLCV (candlestick) data using familiar CCXT methods.

Usage:
    python scripts/gmx/gmx_ccxt_example.py

Requirements:
    - Web3 connection to Arbitrum network
    - No wallet/private key required (read-only operations)
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from web3 import Web3
from eth_defi.gmx.config import GMXConfig
from eth_defi.gmx.ccxt import GMXCCXTWrapper


async def fetch_ohlcv_example():
    """
    Example 1: Basic OHLCV fetching - Similar to Hyperliquid/CCXT usage
    """
    print("=" * 80)
    print("Example 1: Fetch OHLCV Data (CCXT-style)")
    print("=" * 80)

    # Setup GMX connection (Arbitrum mainnet)
    web3 = Web3(Web3.HTTPProvider("https://arb1.arbitrum.io/rpc"))
    config = GMXConfig(web3)

    # Create CCXT-compatible wrapper
    exchange = GMXCCXTWrapper(config)

    # Load available markets (like CCXT)
    print("\nLoading markets...")
    markets = await exchange.load_markets()
    print(f"Loaded {len(markets)} markets")
    print(f"Available markets: {list(markets.keys())[:5]}...")  # Show first 5

    # Fetch OHLCV data for ETH/USD
    print("\n" + "-" * 80)
    print("Fetching ETH/USD hourly candles (last 10)...")
    print("-" * 80)

    symbol = "ETH/USD"
    timeframe = "1h"
    limit = 10

    ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

    print(f"\nReceived {len(ohlcv)} candles for {symbol} ({timeframe})")
    print("\nFormat: [timestamp_ms, open, high, low, close, volume]")
    print("-" * 80)

    # Display the candles
    for i, candle in enumerate(ohlcv[-5:], 1):  # Show last 5
        timestamp_ms, open_price, high, low, close, volume = candle
        from datetime import datetime

        dt = datetime.fromtimestamp(timestamp_ms / 1000)
        print(f"{i}. {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Open: ${open_price:,.2f} | High: ${high:,.2f} | Low: ${low:,.2f} | Close: ${close:,.2f}")
        print(f"   Volume: {volume} (GMX doesn't provide volume data)")

    return ohlcv


async def fetch_multiple_timeframes():
    """
    Example 2: Fetch data for multiple timeframes
    """
    print("\n\n" + "=" * 80)
    print("Example 2: Multiple Timeframes")
    print("=" * 80)

    web3 = Web3(Web3.HTTPProvider("https://arb1.arbitrum.io/rpc"))
    config = GMXConfig(web3)
    exchange = GMXCCXTWrapper(config)

    await exchange.load_markets()

    symbol = "BTC/USD"
    timeframes = ["1m", "15m", "1h", "1d"]

    print(f"\nFetching {symbol} data for multiple timeframes...")

    for tf in timeframes:
        ohlcv = await exchange.fetch_ohlcv(symbol, tf, limit=5)
        latest = ohlcv[-1] if ohlcv else None

        if latest:
            timestamp_ms, open_price, high, low, close, volume = latest
            from datetime import datetime

            dt = datetime.fromtimestamp(timestamp_ms / 1000)
            print(f"\n{tf:>4} - Latest: {dt.strftime('%Y-%m-%d %H:%M')}")
            print(f"      Close: ${close:,.2f} | High: ${high:,.2f} | Low: ${low:,.2f}")


async def fetch_with_since_parameter():
    """
    Example 3: Fetch historical data using 'since' parameter
    """
    print("\n\n" + "=" * 80)
    print("Example 3: Fetch Data Since Specific Time")
    print("=" * 80)

    web3 = Web3(Web3.HTTPProvider("https://arb1.arbitrum.io/rpc"))
    config = GMXConfig(web3)
    exchange = GMXCCXTWrapper(config)

    await exchange.load_markets()

    symbol = "ETH/USD"
    timeframe = "1h"

    # Calculate 'since' as 24 hours ago
    import time

    twenty_four_hours_ago = int((time.time() - 86400) * 1000)  # milliseconds

    print(f"\nFetching {symbol} {timeframe} candles from last 24 hours...")

    ohlcv = await exchange.fetch_ohlcv(
        symbol,
        timeframe,
        since=twenty_four_hours_ago,
        limit=24,
    )

    print(f"Received {len(ohlcv)} candles")

    if ohlcv:
        first = ohlcv[0]
        last = ohlcv[-1]

        from datetime import datetime

        first_time = datetime.fromtimestamp(first[0] / 1000)
        last_time = datetime.fromtimestamp(last[0] / 1000)

        print(f"\nFirst candle: {first_time.strftime('%Y-%m-%d %H:%M')} - Close: ${first[4]:,.2f}")
        print(f"Last candle:  {last_time.strftime('%Y-%m-%d %H:%M')} - Close: ${last[4]:,.2f}")

        # Calculate price change
        price_change = ((last[4] - first[4]) / first[4]) * 100
        print(f"\n24h Price Change: {price_change:+.2f}%")


async def compare_multiple_tokens():
    """
    Example 4: Compare multiple tokens (like okex example)
    """
    print("\n\n" + "=" * 80)
    print("Example 4: Compare Multiple Tokens")
    print("=" * 80)

    web3 = Web3(Web3.HTTPProvider("https://arb1.arbitrum.io/rpc"))
    config = GMXConfig(web3)
    exchange = GMXCCXTWrapper(config)

    await exchange.load_markets()

    symbols = ["ETH/USD", "BTC/USD", "ARB/USD"]
    timeframe = "1d"

    print(f"\nFetching daily data for multiple tokens...")
    print("-" * 80)

    for symbol in symbols:
        try:
            ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=2)

            if len(ohlcv) >= 2:
                yesterday = ohlcv[-2]
                today = ohlcv[-1]

                yesterday_close = yesterday[4]
                today_close = today[4]
                change = ((today_close - yesterday_close) / yesterday_close) * 100

                print(f"\n{symbol:>10}")
                print(f"  Yesterday: ${yesterday_close:>10,.2f}")
                print(f"  Today:     ${today_close:>10,.2f}")
                print(f"  Change:    {change:>10.2f}%")
        except Exception as e:
            print(f"\n{symbol:>10} - Error: {e}")


async def main():
    """
    Run all examples
    """
    print("\n" + "=" * 80)
    print("GMX CCXT-Compatible Interface Examples")
    print("=" * 80)
    print("\nThese examples demonstrate how to use GMX with CCXT-style methods,")
    print("making it easy to migrate from centralized exchanges to GMX protocol.")
    print("=" * 80)

    try:
        # Run examples
        await fetch_ohlcv_example()
        await fetch_multiple_timeframes()
        await fetch_with_since_parameter()
        await compare_multiple_tokens()

        print("\n\n" + "=" * 80)
        print("All examples completed successfully!")
        print("=" * 80)
        print("\nKey Takeaways:")
        print("1. Use load_markets() before fetching data (just like CCXT)")
        print("2. fetch_ohlcv() returns [[timestamp_ms, O, H, L, C, V], ...]")
        print("3. Volume is None (GMX API doesn't provide volume)")
        print("4. Supports timeframes: 1m, 5m, 15m, 1h, 4h, 1d")
        print("5. Use 'since' parameter for historical data (in milliseconds)")
        print("6. Use 'limit' parameter to control number of candles")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
