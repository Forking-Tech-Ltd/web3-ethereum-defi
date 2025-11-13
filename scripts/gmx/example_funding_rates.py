#!/usr/bin/env python3
"""
Funding rate analysis example.

Fetches current funding rates with long/short breakdowns and projects to daily/annual rates.
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

    symbols = ["ETH/USD", "BTC/USD", "ARB/USD"]

    print("Fetching funding rates for multiple markets...\n")
    print("GMX Funding Rates (Hourly)")
    print(f"{'Market':5} {'Long Rate':>12} {'Short Rate':>12} {'Daily (Long)':>14} {'Annual (Long)':>15} {'Direction':>20}")
    print("-" * 90)

    for symbol in symbols:
        try:
            fr = exchange.fetch_funding_rate(symbol)

            long_rate = fr["longFundingRate"]
            short_rate = fr["shortFundingRate"]

            # Project to daily and annual
            long_daily = long_rate * 24
            long_annual = long_rate * 24 * 365

            if long_rate > 0:
                direction = "Longs pay Shorts"
            elif long_rate < 0:
                direction = "Shorts pay Longs"
            else:
                direction = "Balanced"

            token = symbol.replace("/USD", "")
            print(f"{token:5} {long_rate * 100:>11.4f}% {short_rate * 100:>11.4f}% {long_daily * 100:>13.3f}% {long_annual * 100:>14.2f}% {direction:>20}")

        except Exception as e:
            print(f"Error fetching funding rate for {symbol}: {e}")


if __name__ == "__main__":
    main()
