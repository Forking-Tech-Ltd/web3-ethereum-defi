#!/usr/bin/env python3
"""
Open interest analysis example.

Fetches current open interest data with long/short position breakdowns.
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

    print("Fetching open interest for multiple markets...\n")
    print("GMX Open Interest")
    print(f"{'Market':5} {'Long OI':>15} {'Short OI':>15} {'Total OI':>15} {'Long %':>8} {'Skew':>10}")
    print("-" * 80)

    for symbol in symbols:
        try:
            oi = exchange.fetch_open_interest(symbol)

            long_oi = oi["longOpenInterest"]
            short_oi = oi["shortOpenInterest"]
            total_oi = oi["openInterestValue"]

            long_pct = (long_oi / total_oi * 100) if total_oi > 0 else 0
            skew = long_oi - short_oi

            if skew > 0:
                skew_dir = "Long"
            elif skew < 0:
                skew_dir = "Short"
            else:
                skew_dir = "Balanced"

            token = symbol.replace("/USD", "")
            print(f"{token:5} ${long_oi:>14,.0f} ${short_oi:>14,.0f} ${total_oi:>14,.0f} {long_pct:>7.1f}% {skew_dir:>10}")

        except Exception as e:
            print(f"Error fetching OI for {symbol}: {e}")


if __name__ == "__main__":
    main()
