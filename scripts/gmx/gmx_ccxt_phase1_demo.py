#!/usr/bin/env python3
"""
GMX CCXT Phase 1 - Market Data Demo

Demonstrates all Phase 1 CCXT-compatible market data methods:
- fetch_ticker() - Single market ticker
- fetch_tickers() - Multiple market tickers
- fetch_currencies() - Token metadata
- fetch_trades() - Recent public trades
- fetch_time() - Server/blockchain time
- fetch_status() - API health status

Usage:
    python scripts/gmx/gmx_ccxt_phase1_demo.py
"""

import os
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from web3 import Web3

from eth_defi.gmx.config import GMXConfig
from eth_defi.gmx.ccxt import GMXCCXT

console = Console()


def demo_fetch_ticker(gmx: GMXCCXT):
    """Demo fetch_ticker() - Single market ticker"""
    console.print("\n[bold cyan]1. fetch_ticker() - Single Market Ticker[/bold cyan]")
    console.print("Fetching ticker for ETH/USD...\n")

    ticker = gmx.fetch_ticker("ETH/USD")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan")
    table.add_column("Value", justify="right")

    table.add_row("Symbol", str(ticker['symbol']))
    table.add_row("Last Price", f"${ticker['last']:,.2f}" if ticker['last'] else "N/A")
    table.add_row("24h High", f"${ticker['high']:,.2f}" if ticker['high'] else "N/A")
    table.add_row("24h Low", f"${ticker['low']:,.2f}" if ticker['low'] else "N/A")
    table.add_row("24h Open", f"${ticker['open']:,.2f}" if ticker['open'] else "N/A")
    table.add_row("Timestamp", ticker['datetime'])

    console.print(table)


def demo_fetch_tickers(gmx: GMXCCXT):
    """Demo fetch_tickers() - Multiple market tickers"""
    console.print("\n[bold cyan]2. fetch_tickers() - Multiple Market Tickers[/bold cyan]")
    console.print("Fetching tickers for all markets...\n")

    tickers = gmx.fetch_tickers()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Symbol", style="cyan")
    table.add_column("Last Price", justify="right")
    table.add_column("24h High", justify="right")
    table.add_column("24h Low", justify="right")

    for symbol in sorted(tickers.keys())[:10]:  # Show first 10
        ticker = tickers[symbol]
        last = f"${ticker['last']:,.2f}" if ticker['last'] else "N/A"
        high = f"${ticker['high']:,.2f}" if ticker['high'] else "N/A"
        low = f"${ticker['low']:,.2f}" if ticker['low'] else "N/A"

        table.add_row(symbol, last, high, low)

    console.print(table)
    console.print(f"\n[dim]Total markets: {len(tickers)}[/dim]")

    # Demo filtering by symbols
    console.print("\n[bold]Filtering to specific symbols (ETH/USD, BTC/USD):[/bold]")
    filtered = gmx.fetch_tickers(["ETH/USD", "BTC/USD"])
    for symbol, ticker in filtered.items():
        console.print(f"  {symbol}: ${ticker['last']:,.2f}")


def demo_fetch_currencies(gmx: GMXCCXT):
    """Demo fetch_currencies() - Token metadata"""
    console.print("\n[bold cyan]3. fetch_currencies() - Token Metadata[/bold cyan]")
    console.print("Fetching currency metadata...\n")

    currencies = gmx.fetch_currencies()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Code", style="cyan")
    table.add_column("Name")
    table.add_column("Decimals", justify="right")
    table.add_column("Address", style="dim")

    for code in sorted(currencies.keys())[:10]:  # Show first 10
        currency = currencies[code]
        name = currency['name'][:20]  # Truncate long names
        decimals = str(currency['precision'])
        address = currency['id'][:10] + "..." + currency['id'][-6:]  # Shorten address

        table.add_row(code, name, decimals, address)

    console.print(table)
    console.print(f"\n[dim]Total currencies: {len(currencies)}[/dim]")


def demo_fetch_trades(gmx: GMXCCXT):
    """Demo fetch_trades() - Recent public trades"""
    console.print("\n[bold cyan]4. fetch_trades() - Recent Public Trades[/bold cyan]")
    console.print("Fetching recent trades for ETH/USD (last 24 hours)...\n")

    # Get trades from last 24 hours
    since = int((datetime.now() - timedelta(hours=24)).timestamp() * 1000)
    trades = gmx.fetch_trades("ETH/USD", since=since, limit=10)

    if trades:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Time", style="cyan")
        table.add_column("Side")
        table.add_column("Price", justify="right")
        table.add_column("Amount", justify="right")
        table.add_column("Cost", justify="right")

        for trade in trades[:10]:  # Show first 10
            timestamp = datetime.fromisoformat(trade['datetime'].replace('Z', '+00:00'))
            time_str = timestamp.strftime('%m-%d %H:%M')
            side_style = "green" if trade['side'] == "buy" else "red"
            side = f"[{side_style}]{trade['side'].upper()}[/{side_style}]"
            price = f"${trade['price']:,.2f}" if trade['price'] else "N/A"
            amount = f"{trade['amount']:.4f}" if trade['amount'] else "N/A"
            cost = f"${trade['cost']:,.2f}" if trade['cost'] else "N/A"

            table.add_row(time_str, side, price, amount, cost)

        console.print(table)
        console.print(f"\n[dim]Total trades: {len(trades)}[/dim]")
    else:
        console.print("[yellow]No trades found in the last 24 hours[/yellow]")


def demo_fetch_time(gmx: GMXCCXT):
    """Demo fetch_time() - Server/blockchain time"""
    console.print("\n[bold cyan]5. fetch_time() - Server/Blockchain Time[/bold cyan]")
    console.print("Fetching blockchain time...\n")

    server_time = gmx.fetch_time()
    dt = datetime.fromtimestamp(server_time / 1000)

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan")
    table.add_column("Value")

    table.add_row("Server Time (ms)", f"{server_time:,}")
    table.add_row("Readable Time", dt.strftime('%Y-%m-%d %H:%M:%S'))

    # Compare with local time
    local_time = datetime.now()
    diff_seconds = abs((dt - local_time).total_seconds())
    table.add_row("Local Time", local_time.strftime('%Y-%m-%d %H:%M:%S'))
    table.add_row("Difference", f"{diff_seconds:.2f} seconds")

    console.print(table)


def demo_fetch_status(gmx: GMXCCXT):
    """Demo fetch_status() - API health status"""
    console.print("\n[bold cyan]6. fetch_status() - API Health Status[/bold cyan]")
    console.print("Checking API status...\n")

    status = gmx.fetch_status()

    # Create status panel
    status_color = "green" if status['status'] == 'ok' else "red"
    status_text = f"[{status_color}]{status['status'].upper()}[/{status_color}]"

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan")
    table.add_column("Status")

    table.add_row("Overall Status", status_text)
    table.add_row("GMX API", status['info'].get('gmx_api', 'N/A'))
    table.add_row("Subsquid", status['info'].get('subsquid', 'N/A'))
    table.add_row("Web3", status['info'].get('web3', 'N/A'))

    if 'web3_block_number' in status['info']:
        table.add_row("Current Block", f"{status['info']['web3_block_number']:,}")

    console.print(table)
    console.print(f"\n[dim]Updated: {status['datetime']}[/dim]")


def main():
    console.print(Panel.fit(
        "[bold cyan]GMX CCXT Phase 1 - Market Data Demo[/bold cyan]\n"
        "Demonstrating all CCXT-compatible market data methods",
        border_style="cyan"
    ))

    # Initialize GMX CCXT wrapper
    rpc = os.environ.get("JSON_RPC_ARBITRUM")
    if not rpc:
        console.print("[yellow]Warning: JSON_RPC_ARBITRUM not found, using default RPC[/yellow]")
        rpc = "https://arb1.arbitrum.io/rpc"

    console.print(f"\n[dim]Connecting to Arbitrum: {rpc}[/dim]")
    web3 = Web3(Web3.HTTPProvider(rpc))
    config = GMXConfig(web3)
    gmx = GMXCCXT(config)

    console.print(f"[dim]Chain ID: {web3.eth.chain_id}[/dim]")
    console.print("[green]✓ Connected successfully[/green]")

    try:
        # Run all demos
        demo_fetch_ticker(gmx)
        demo_fetch_tickers(gmx)
        demo_fetch_currencies(gmx)
        demo_fetch_trades(gmx)
        demo_fetch_time(gmx)
        demo_fetch_status(gmx)

        console.print("\n" + "=" * 60)
        console.print("[bold green]✓ All Phase 1 methods demonstrated successfully![/bold green]")
        console.print("=" * 60)

    except Exception as e:
        console.print(f"\n[bold red]✗ Error: {e}[/bold red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise


if __name__ == "__main__":
    main()
