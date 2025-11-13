#!/usr/bin/env python3
"""
Historical funding rates example.

Demonstrates fetching historical funding rate data from GMX Subsquid GraphQL endpoint.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from web3 import Web3
from eth_defi.gmx.config import GMXConfig
from eth_defi.gmx.ccxt import GMXCCXTWrapper


def main():
    # Connect to Arbitrum
    web3 = Web3(Web3.HTTPProvider("https://arb1.arbitrum.io/rpc"))
    config = GMXConfig(web3)
    exchange = GMXCCXTWrapper(config)

    exchange.load_markets()

    # Get market address for BTC/USD
    market = exchange.markets.get("BTC/USD")
    if not market:
        print("BTC/USD market not found")
        return

    market_address = market["info"]["market_token"]

    print("Fetching historical funding rates for BTC/USD...\n")

    # Fetch historical funding rate data from Subsquid
    history = exchange.fetch_funding_rate_history(
        "BTC/USD",
        limit=10,
        params={"market_address": market_address}
    )

    print(f"Retrieved {len(history)} historical snapshots\n")
    print(f"{'Index':>6} {'Hourly Rate':>13} {'Daily Rate':>12} {'Annual Rate':>13} {'Direction':>20}")
    print("-" * 75)

    for idx, snapshot in enumerate(history):
        # Funding rate is per second, convert to hourly/daily/annual
        per_second = snapshot["fundingRate"]
        hourly = per_second * 3600
        daily = hourly * 24
        annual = daily * 365

        long_rate = snapshot["longFundingRate"]
        if long_rate > 0:
            direction = "Longs pay Shorts"
        elif long_rate < 0:
            direction = "Shorts pay Longs"
        else:
            direction = "Balanced"

        print(f"{idx:>6} {hourly * 100:>12.4f}% {daily * 100:>11.3f}% {annual * 100:>12.2f}% {direction:>20}")

    if history:
        print(f"\nNote: Data fetched from GMX Subsquid GraphQL endpoint")
        print(f"Market Address: {market_address}")
        print(f"Rates are converted from per-second values")


if __name__ == "__main__":
    main()
