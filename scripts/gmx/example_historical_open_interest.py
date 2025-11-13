#!/usr/bin/env python3
"""
Historical open interest example.

Demonstrates fetching historical open interest data from GMX Subsquid GraphQL endpoint.
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

    # Get market address for ETH/USD
    market = exchange.markets.get("ETH/USD")
    if not market:
        print("ETH/USD market not found")
        return

    market_address = market["info"]["market_token"]

    print("Fetching historical open interest for ETH/USD...\n")

    # Fetch historical OI data from Subsquid
    history = exchange.fetch_open_interest_history(
        "ETH/USD",
        limit=10,
        params={"market_address": market_address}
    )

    print(f"Retrieved {len(history)} historical snapshots\n")
    print(f"{'Index':>6} {'Total OI':>15} {'Long OI':>15} {'Short OI':>15} {'Long %':>8}")
    print("-" * 70)

    for idx, snapshot in enumerate(history):
        total_oi = snapshot["openInterestValue"]
        long_oi = snapshot["longOpenInterest"]
        short_oi = snapshot["shortOpenInterest"]
        long_pct = (long_oi / total_oi * 100) if total_oi > 0 else 0

        print(f"{idx:>6} ${total_oi:>14,.0f} ${long_oi:>14,.0f} ${short_oi:>14,.0f} {long_pct:>7.1f}%")

    if history:
        print(f"\nNote: Data fetched from GMX Subsquid GraphQL endpoint")
        print(f"Market Address: {market_address}")


if __name__ == "__main__":
    main()
