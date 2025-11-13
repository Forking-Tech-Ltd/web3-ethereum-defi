#!/usr/bin/env python3
"""
Fetch markets example.

Demonstrates fetching all available markets from GMX without caching.
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

    # Fetch markets (returns list, does not cache)
    print("Fetching markets from GMX...\n")
    markets = exchange.fetch_markets()

    print(f"Found {len(markets)} markets\n")
    print(f"{'Symbol':12} {'Base':8} {'Quote':8} {'Type':8} {'Active':8}")
    print("-" * 50)

    for market in markets:
        symbol = market["symbol"]
        base = market["base"]
        quote = market["quote"]
        mtype = market["type"]
        active = "Yes" if market["active"] else "No"

        print(f"{symbol:12} {base:8} {quote:8} {mtype:8} {active:8}")


if __name__ == "__main__":
    main()
