#!/usr/bin/env python3
"""
GMX CCXT Interface Example

This script demonstrates how to use the CCXT-compatible interface for GMX protocol.
It shows how to fetch OHLCV (candlestick) data and analyze it using pandas, numpy,
and rich for beautiful console output.

Usage::

    python scripts/gmx/gmx_ccxt_example.py

.. note::
    Requirements:
    - Web3 connection to Arbitrum network
    - No wallet/private key required (read-only operations)
"""

import sys
from pathlib import Path
import time
from datetime import datetime

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from web3 import Web3
from eth_defi.gmx.config import GMXConfig
from eth_defi.gmx.ccxt import GMXCCXTWrapper

import pandas as pd
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
from rich import box

console = Console()


def ohlcv_to_dataframe(ohlcv, symbol):
    """
    Convert OHLCV list to pandas DataFrame.

    :param ohlcv: List of OHLCV candles
    :type ohlcv: List[List]
    :param symbol: Trading pair symbol
    :type symbol: str
    :returns: DataFrame with OHLCV data and symbol column
    :rtype: pd.DataFrame
    """
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["symbol"] = symbol
    return df


def calculate_technical_indicators(df):
    """
    Calculate basic technical indicators.

    :param df: DataFrame with OHLCV data
    :type df: pd.DataFrame
    :returns: DataFrame with added technical indicator columns
    :rtype: pd.DataFrame
    """
    # Simple Moving Averages
    df["sma_10"] = df["close"].rolling(window=10).mean()
    df["sma_20"] = df["close"].rolling(window=20).mean()

    # Price changes
    df["change"] = df["close"].diff()
    df["change_pct"] = df["close"].pct_change() * 100

    # High-Low range
    df["hl_range"] = df["high"] - df["low"]
    df["hl_range_pct"] = (df["hl_range"] / df["close"]) * 100

    return df


def fetch_ohlcv_example():
    """
    Example 1: Basic OHLCV fetching with DataFrame analysis.

    Demonstrates how to fetch OHLCV data for a single symbol,
    convert to DataFrame, and calculate technical indicators.

    :returns: DataFrame with OHLCV data and indicators
    :rtype: pd.DataFrame
    """
    console.print(Panel.fit(
        "[bold cyan]Example 1: Fetch OHLCV Data (CCXT-style)[/bold cyan]",
        border_style="cyan"
    ))

    # Setup GMX connection (Arbitrum mainnet)
    web3 = Web3(Web3.HTTPProvider("https://arb1.arbitrum.io/rpc"))
    config = GMXConfig(web3)

    # Create CCXT-compatible wrapper
    exchange = GMXCCXTWrapper(config)

    # Load available markets
    console.print("\n[yellow]Loading markets...[/yellow]")
    markets = exchange.load_markets()
    console.print(f"[green]✓[/green] Loaded {len(markets)} markets")

    # Fetch OHLCV data for ETH/USD
    console.print("\n" + "─" * 80)
    console.print("[bold]Fetching ETH/USD hourly candles (last 50)...[/bold]")
    console.print("─" * 80 + "\n")

    symbol = "ETH/USD"
    timeframe = "1h"
    limit = 50

    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

    # Convert to DataFrame
    df = ohlcv_to_dataframe(ohlcv, symbol)
    df = calculate_technical_indicators(df)

    console.print(f"[green]✓[/green] Received {len(ohlcv)} candles for {symbol} ({timeframe})\n")

    # Display statistics table
    stats_table = Table(title=f"📊 {symbol} Statistics", box=box.ROUNDED)
    stats_table.add_column("Metric", style="cyan", justify="left")
    stats_table.add_column("Value", style="green", justify="right")

    latest = df.iloc[-1]
    stats_table.add_row("Latest Price", f"${latest['close']:,.2f}")
    stats_table.add_row("24h High", f"${df['high'].tail(24).max():,.2f}")
    stats_table.add_row("24h Low", f"${df['low'].tail(24).min():,.2f}")
    stats_table.add_row("24h Change", f"{df['change_pct'].tail(24).sum():+.2f}%")
    stats_table.add_row("Avg HL Range", f"${df['hl_range'].mean():.2f}")
    stats_table.add_row("SMA 10", f"${latest['sma_10']:.2f}")
    stats_table.add_row("SMA 20", f"${latest['sma_20']:.2f}")

    console.print(stats_table)

    # Display recent candles
    console.print("\n")
    candles_table = Table(title="🕯️  Recent Candles (Last 5)", box=box.SIMPLE)
    candles_table.add_column("Time", style="cyan")
    candles_table.add_column("Open", justify="right")
    candles_table.add_column("High", justify="right", style="green")
    candles_table.add_column("Low", justify="right", style="red")
    candles_table.add_column("Close", justify="right", style="bold")
    candles_table.add_column("Change %", justify="right")

    for _, row in df.tail(5).iterrows():
        change_style = "green" if row["change_pct"] >= 0 else "red"
        candles_table.add_row(
            row["timestamp"].strftime("%m-%d %H:%M"),
            f"${row['open']:,.2f}",
            f"${row['high']:,.2f}",
            f"${row['low']:,.2f}",
            f"${row['close']:,.2f}",
            f"[{change_style}]{row['change_pct']:+.2f}%[/{change_style}]",
        )

    console.print(candles_table)

    return df


def fetch_multiple_timeframes():
    """
    Example 2: Fetch and compare multiple timeframes.

    Demonstrates how to fetch OHLCV data across different timeframes
    and compare price movements and volatility.
    """
    console.print("\n\n")
    console.print(Panel.fit(
        "[bold cyan]Example 2: Multiple Timeframes Analysis[/bold cyan]",
        border_style="cyan"
    ))

    web3 = Web3(Web3.HTTPProvider("https://arb1.arbitrum.io/rpc"))
    config = GMXConfig(web3)
    exchange = GMXCCXTWrapper(config)

    exchange.load_markets()

    symbol = "BTC/USD"
    timeframes = ["1m", "15m", "1h", "1d"]

    console.print(f"\n[yellow]Fetching {symbol} data for multiple timeframes...[/yellow]\n")

    # Create comparison table
    tf_table = Table(title=f"📈 {symbol} Multi-Timeframe Analysis", box=box.ROUNDED)
    tf_table.add_column("Timeframe", style="cyan", justify="center")
    tf_table.add_column("Latest Price", justify="right")
    tf_table.add_column("Change %", justify="right")
    tf_table.add_column("High", justify="right", style="green")
    tf_table.add_column("Low", justify="right", style="red")
    tf_table.add_column("Volatility", justify="right")

    for tf in track(timeframes, description="Loading..."):
        ohlcv = exchange.fetch_ohlcv(symbol, tf, limit=10)
        df = ohlcv_to_dataframe(ohlcv, symbol)
        df = calculate_technical_indicators(df)

        latest = df.iloc[-1]
        first = df.iloc[0]
        change_pct = ((latest["close"] - first["close"]) / first["close"]) * 100
        volatility = df["hl_range_pct"].mean()

        change_style = "green" if change_pct >= 0 else "red"
        tf_table.add_row(
            tf,
            f"${latest['close']:,.2f}",
            f"[{change_style}]{change_pct:+.2f}%[/{change_style}]",
            f"${df['high'].max():,.2f}",
            f"${df['low'].min():,.2f}",
            f"{volatility:.2f}%",
        )

    console.print(tf_table)


def fetch_with_since_parameter():
    """
    Example 3: Fetch historical data and calculate returns.

    Demonstrates how to use the 'since' parameter to fetch data
    from a specific timestamp and calculate performance metrics.
    """
    console.print("\n\n")
    console.print(Panel.fit(
        "[bold cyan]Example 3: Historical Analysis with 'since' Parameter[/bold cyan]",
        border_style="cyan"
    ))

    web3 = Web3(Web3.HTTPProvider("https://arb1.arbitrum.io/rpc"))
    config = GMXConfig(web3)
    exchange = GMXCCXTWrapper(config)

    exchange.load_markets()

    symbol = "ETH/USD"
    timeframe = "1h"

    # Calculate 'since' as 24 hours ago
    twenty_four_hours_ago = int((time.time() - 86400) * 1000)  # milliseconds

    console.print(f"\n[yellow]Fetching {symbol} {timeframe} candles from last 24 hours...[/yellow]\n")

    ohlcv = exchange.fetch_ohlcv(
        symbol,
        timeframe,
        since=twenty_four_hours_ago,
        limit=24,
    )

    df = ohlcv_to_dataframe(ohlcv, symbol)
    df = calculate_technical_indicators(df)

    # Calculate performance metrics
    first_price = df.iloc[0]["close"]
    last_price = df.iloc[-1]["close"]
    price_change = last_price - first_price
    price_change_pct = (price_change / first_price) * 100

    max_price = df["high"].max()
    min_price = df["low"].min()
    avg_price = df["close"].mean()
    std_dev = df["close"].std()

    # Display performance panel
    perf_table = Table(title=f"📊 24-Hour Performance: {symbol}", box=box.ROUNDED)
    perf_table.add_column("Metric", style="cyan", justify="left")
    perf_table.add_column("Value", style="bold", justify="right")

    perf_table.add_row("Start Price", f"${first_price:,.2f}")
    perf_table.add_row("End Price", f"${last_price:,.2f}")

    change_style = "green" if price_change >= 0 else "red"
    perf_table.add_row(
        "24h Change",
        f"[{change_style}]{price_change:+,.2f} ({price_change_pct:+.2f}%)[/{change_style}]"
    )

    perf_table.add_row("─" * 20, "─" * 15)
    perf_table.add_row("24h High", f"${max_price:,.2f}")
    perf_table.add_row("24h Low", f"${min_price:,.2f}")
    perf_table.add_row("Average", f"${avg_price:,.2f}")
    perf_table.add_row("Std Dev", f"${std_dev:.2f}")
    perf_table.add_row("Volatility", f"{(std_dev / avg_price * 100):.2f}%")

    console.print(perf_table)


def compare_multiple_tokens():
    """
    Example 4: Compare multiple tokens with correlation analysis.

    Demonstrates how to fetch data for multiple symbols simultaneously,
    compare their performance, and calculate price correlations.
    """
    console.print("\n\n")
    console.print(Panel.fit(
        "[bold cyan]Example 4: Multi-Token Comparison & Correlation[/bold cyan]",
        border_style="cyan"
    ))

    web3 = Web3(Web3.HTTPProvider("https://arb1.arbitrum.io/rpc"))
    config = GMXConfig(web3)
    exchange = GMXCCXTWrapper(config)

    exchange.load_markets()

    symbols = ["ETH/USD", "BTC/USD", "ARB/USD"]
    timeframe = "1h"
    limit = 24

    console.print(f"\n[yellow]Fetching hourly data for {len(symbols)} tokens...[/yellow]\n")

    # Collect data for all symbols
    dfs = {}
    for symbol in track(symbols, description="Loading..."):
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = ohlcv_to_dataframe(ohlcv, symbol)
            df = calculate_technical_indicators(df)
            dfs[symbol] = df
        except Exception as e:
            console.print(f"[red]Error fetching {symbol}: {e}[/red]")

    # Create comparison table
    comp_table = Table(title="💰 Token Comparison (24h)", box=box.ROUNDED)
    comp_table.add_column("Token", style="cyan", justify="left")
    comp_table.add_column("Current Price", justify="right")
    comp_table.add_column("24h Change", justify="right")
    comp_table.add_column("24h Return %", justify="right")
    comp_table.add_column("Volatility", justify="right")
    comp_table.add_column("Trend", justify="center")

    for symbol, df in dfs.items():
        if len(df) >= 2:
            first_price = df.iloc[0]["close"]
            latest_price = df.iloc[-1]["close"]
            change = latest_price - first_price
            change_pct = (change / first_price) * 100
            volatility = df["hl_range_pct"].mean()

            # Determine trend based on SMA
            sma_10 = df["sma_10"].iloc[-1]
            sma_20 = df["sma_20"].iloc[-1]
            if pd.notna(sma_10) and pd.notna(sma_20):
                if sma_10 > sma_20:
                    trend = "📈 Bullish"
                    trend_style = "green"
                else:
                    trend = "📉 Bearish"
                    trend_style = "red"
            else:
                trend = "➡️  Neutral"
                trend_style = "yellow"

            change_style = "green" if change >= 0 else "red"
            comp_table.add_row(
                symbol.replace("/USD", ""),
                f"${latest_price:,.2f}",
                f"[{change_style}]${change:+,.2f}[/{change_style}]",
                f"[{change_style}]{change_pct:+.2f}%[/{change_style}]",
                f"{volatility:.2f}%",
                f"[{trend_style}]{trend}[/{trend_style}]",
            )

    console.print(comp_table)

    # Calculate correlation matrix if we have enough data
    if len(dfs) >= 2:
        console.print("\n")
        corr_table = Table(title="🔗 Price Correlation Matrix", box=box.ROUNDED)
        corr_table.add_column("", style="cyan")

        # Prepare data for correlation
        price_data = {}
        for symbol, df in dfs.items():
            token = symbol.replace("/USD", "")
            price_data[token] = df["close"].values
            corr_table.add_column(token, justify="center")

        # Calculate correlations
        tokens = list(price_data.keys())
        for token1 in tokens:
            row = [token1]
            for token2 in tokens:
                if token1 == token2:
                    row.append("[bold]1.00[/bold]")
                else:
                    # Calculate correlation
                    corr = np.corrcoef(price_data[token1], price_data[token2])[0, 1]
                    if corr > 0.7:
                        style = "green"
                    elif corr < 0.3:
                        style = "red"
                    else:
                        style = "yellow"
                    row.append(f"[{style}]{corr:.2f}[/{style}]")
            corr_table.add_row(*row)

        console.print(corr_table)


def fetch_open_interest_example():
    """
    Example 5: Fetch open interest for multiple markets.

    Demonstrates how to fetch current open interest data
    with long/short position breakdowns and calculate position skew.
    """
    console.print("\n\n")
    console.print(Panel.fit(
        "[bold cyan]Example 5: Open Interest Analysis[/bold cyan]",
        border_style="cyan"
    ))

    web3 = Web3(Web3.HTTPProvider("https://arb1.arbitrum.io/rpc"))
    config = GMXConfig(web3)
    exchange = GMXCCXTWrapper(config)

    exchange.load_markets()

    symbols = ["ETH/USD", "BTC/USD", "ARB/USD"]

    console.print(f"\n[yellow]Fetching open interest for {len(symbols)} markets...[/yellow]\n")

    # Create table for open interest
    oi_table = Table(title="📊 GMX Open Interest", box=box.ROUNDED)
    oi_table.add_column("Market", style="cyan", justify="left")
    oi_table.add_column("Long OI", justify="right", style="green")
    oi_table.add_column("Short OI", justify="right", style="red")
    oi_table.add_column("Total OI", justify="right", style="bold")
    oi_table.add_column("Long %", justify="right")
    oi_table.add_column("Skew", justify="center")

    for symbol in track(symbols, description="Loading..."):
        try:
            oi = exchange.fetch_open_interest(symbol)

            long_oi = oi["longOpenInterest"]
            short_oi = oi["shortOpenInterest"]
            total_oi = oi["openInterestValue"]

            # Calculate long percentage and skew
            long_pct = (long_oi / total_oi * 100) if total_oi > 0 else 0
            skew = long_oi - short_oi

            # Determine skew direction
            if skew > 0:
                skew_indicator = "📈 Long"
                skew_style = "green"
            elif skew < 0:
                skew_indicator = "📉 Short"
                skew_style = "red"
            else:
                skew_indicator = "⚖️  Balanced"
                skew_style = "yellow"

            oi_table.add_row(
                symbol.replace("/USD", ""),
                f"${long_oi:,.0f}",
                f"${short_oi:,.0f}",
                f"${total_oi:,.0f}",
                f"{long_pct:.1f}%",
                f"[{skew_style}]{skew_indicator}[/{skew_style}]",
            )
        except Exception as e:
            console.print(f"[red]Error fetching OI for {symbol}: {e}[/red]")

    console.print(oi_table)

    # Add interpretation note
    console.print("\n[dim]Note: Open interest represents the total value of outstanding positions.[/dim]")
    console.print("[dim]Higher long % indicates more bullish positioning.[/dim]")


def fetch_funding_rates_example():
    """
    Example 6: Fetch funding rates for multiple markets.

    Demonstrates how to fetch current funding rates with long/short breakdowns
    and project hourly rates to daily and annual estimates.
    """
    console.print("\n\n")
    console.print(Panel.fit(
        "[bold cyan]Example 6: Funding Rate Analysis[/bold cyan]",
        border_style="cyan"
    ))

    web3 = Web3(Web3.HTTPProvider("https://arb1.arbitrum.io/rpc"))
    config = GMXConfig(web3)
    exchange = GMXCCXTWrapper(config)

    exchange.load_markets()

    symbols = ["ETH/USD", "BTC/USD", "ARB/USD"]

    console.print(f"\n[yellow]Fetching funding rates for {len(symbols)} markets...[/yellow]\n")

    # Create table for funding rates
    fr_table = Table(title="💰 GMX Funding Rates (Hourly)", box=box.ROUNDED)
    fr_table.add_column("Market", style="cyan", justify="left")
    fr_table.add_column("Long Rate", justify="right")
    fr_table.add_column("Short Rate", justify="right")
    fr_table.add_column("Daily (Long)", justify="right")
    fr_table.add_column("Annual (Long)", justify="right")
    fr_table.add_column("Direction", justify="center")

    for symbol in track(symbols, description="Loading..."):
        try:
            fr = exchange.fetch_funding_rate(symbol)

            long_rate = fr["longFundingRate"]
            short_rate = fr["shortFundingRate"]

            # Calculate daily and annual rates (hourly rate * hours)
            long_daily = long_rate * 24  # 24 hours
            long_annual = long_rate * 24 * 365  # Annual

            # Determine who pays whom
            if long_rate > 0:
                direction = "Longs pay Shorts"
                direction_style = "red"
            elif long_rate < 0:
                direction = "Shorts pay Longs"
                direction_style = "green"
            else:
                direction = "Balanced"
                direction_style = "yellow"

            # Style the rates
            long_style = "red" if long_rate > 0 else "green"
            short_style = "red" if short_rate > 0 else "green"

            fr_table.add_row(
                symbol.replace("/USD", ""),
                f"[{long_style}]{long_rate * 100:.4f}%[/{long_style}]",
                f"[{short_style}]{short_rate * 100:.4f}%[/{short_style}]",
                f"{long_daily * 100:+.3f}%",
                f"{long_annual * 100:+.2f}%",
                f"[{direction_style}]{direction}[/{direction_style}]",
            )
        except Exception as e:
            console.print(f"[red]Error fetching funding rate for {symbol}: {e}[/red]")

    console.print(fr_table)

    # Add interpretation note
    console.print("\n[dim]Note: Positive rates mean longs pay shorts (bullish sentiment).[/dim]")
    console.print("[dim]Negative rates mean shorts pay longs (bearish sentiment).[/dim]")
    console.print("[dim]Rates are charged/earned hourly and compound over time.[/dim]")


def main():
    """
    Run all examples.

    Executes all example functions demonstrating the GMX CCXT interface,
    including OHLCV data fetching, open interest, and funding rate analysis.
    """
    console.print("\n")
    console.print(Panel.fit(
        "[bold magenta]GMX CCXT-Compatible Interface Examples[/bold magenta]\n"
        "[dim]Demonstrating CCXT-style methods with pandas, numpy, and rich output[/dim]",
        border_style="magenta",
        padding=(1, 2)
    ))

    try:
        # Run examples
        fetch_ohlcv_example()
        fetch_multiple_timeframes()
        fetch_with_since_parameter()
        compare_multiple_tokens()
        fetch_open_interest_example()
        fetch_funding_rates_example()

        # Summary
        console.print("\n\n")
        console.print(Panel.fit(
            "[bold green]✓ All examples completed successfully![/bold green]\n\n"
            "[cyan]Key Takeaways:[/cyan]\n"
            "• Use [bold]load_markets()[/bold] before fetching data\n"
            "• [bold]fetch_ohlcv()[/bold] returns [[timestamp_ms, O, H, L, C, V], ...]\n"
            "• [bold]fetch_open_interest()[/bold] returns current open interest data\n"
            "• [bold]fetch_funding_rate()[/bold] returns current funding rates\n"
            "• Volume is [yellow]0[/yellow] (GMX API doesn't provide volume)\n"
            "• Supported timeframes: [dim]1m, 5m, 15m, 1h, 4h, 1d[/dim]\n"
            "• Historical OI/funding not available via API (use Subgraph)\n"
            "• Convert to pandas DataFrame for easy analysis",
            border_style="green",
            padding=(1, 2)
        ))

    except Exception as e:
        console.print(f"\n[bold red]❌ Error:[/bold red] {e}")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()
