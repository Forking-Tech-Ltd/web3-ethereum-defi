#!/usr/bin/env python3
"""
GMX CCXT Position Management Examples

Examples of CCXT-compatible position management methods:
- fetch_positions() - Detailed position information with metrics
- set_leverage() - Configure leverage settings
- fetch_leverage() - Query leverage configuration

Note: add_margin() and reduce_margin() require smart contract integration
and are not included.

Usage:
    export WALLET_ADDRESS="0xYourAddress"
    export JSON_RPC_ARBITRUM="https://arb1.arbitrum.io/rpc"
    python scripts/gmx/gmx_ccxt_positions.py
"""

import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from web3 import Web3

from eth_defi.gmx.config import GMXConfig
from eth_defi.gmx.ccxt import GMXCCXT

console = Console()


def example_fetch_positions(gmx: GMXCCXT):
    """Example:fetch_positions() - Detailed position information"""
    console.print("\n[bold cyan]1. fetch_positions() - Detailed Position Information[/bold cyan]")
    console.print("Fetching open positions with full metrics...\n")

    try:
        positions = gmx.fetch_positions()

        if not positions:
            console.print("[yellow]No open positions found[/yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Symbol", style="cyan")
        table.add_column("Side")
        table.add_column("Size", justify="right")
        table.add_column("Entry", justify="right")
        table.add_column("Mark", justify="right")
        table.add_column("Leverage", justify="right")
        table.add_column("PnL", justify="right")
        table.add_column("Liq. Price", justify="right")

        for pos in positions[:10]:  # Show first 10
            symbol = pos['symbol']
            side_style = "green" if pos['side'] == "long" else "red"
            side = f"[{side_style}]{pos['side'].upper()}[/{side_style}]"

            contracts = f"{pos['contracts']:.4f}" if pos['contracts'] else "N/A"
            entry_price = f"${pos['entryPrice']:,.2f}" if pos['entryPrice'] else "N/A"
            mark_price = f"${pos['markPrice']:,.2f}" if pos['markPrice'] else "N/A"
            leverage = f"{pos['leverage']:.2f}x" if pos['leverage'] else "N/A"

            # PnL with color
            unrealized_pnl = pos.get('unrealizedPnl')
            percentage = pos.get('percentage')
            if unrealized_pnl is not None and percentage is not None:
                pnl_color = "green" if unrealized_pnl >= 0 else "red"
                pnl_str = f"[{pnl_color}]${unrealized_pnl:,.2f} ({percentage:.2f}%)[/{pnl_color}]"
            else:
                pnl_str = "N/A"

            liq_price = f"${pos['liquidationPrice']:,.2f}" if pos['liquidationPrice'] else "N/A"

            table.add_row(symbol, side, contracts, entry_price, mark_price, leverage, pnl_str, liq_price)

        console.print(table)
        console.print(f"\n[dim]Total positions: {len(positions)}[/dim]")

        # Example:filtering by symbols
        if len(positions) > 0:
            first_symbol = positions[0]['symbol']
            console.print(f"\n[bold]Filtering to {first_symbol}:[/bold]")
            filtered = gmx.fetch_positions(symbols=[first_symbol])
            console.print(f"Found {len(filtered)} position(s) for {first_symbol}")

            # Show detailed metrics for first position
            if filtered:
                pos = filtered[0]
                console.print("\n[bold]Position Metrics:[/bold]")
                metrics = Table(show_header=False)
                metrics.add_column("Field", style="cyan")
                metrics.add_column("Value")

                metrics.add_row("Contracts", f"{pos['contracts']:.6f}" if pos['contracts'] else "N/A")
                metrics.add_row("Notional", f"${pos['notional']:,.2f}" if pos['notional'] else "N/A")
                metrics.add_row("Collateral", f"${pos['collateral']:,.2f}" if pos['collateral'] else "N/A")
                metrics.add_row("Initial Margin", f"${pos['initialMargin']:,.2f}" if pos['initialMargin'] else "N/A")
                metrics.add_row("Maintenance Margin", f"${pos['maintenanceMargin']:,.2f}" if pos['maintenanceMargin'] else "N/A")
                metrics.add_row("Margin Ratio", f"{pos['marginRatio']:.4f}" if pos['marginRatio'] else "N/A")

                console.print(metrics)

    except ValueError as e:
        console.print(f"[yellow]Skipped: {e}[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def example_set_leverage(gmx: GMXCCXT):
    """Example:set_leverage() - Configure leverage settings"""
    console.print("\n[bold cyan]2. set_leverage() - Configure Leverage Settings[/bold cyan]")
    console.print("Setting leverage for trading...\n")

    try:
        # Set leverage for specific symbol
        console.print("[bold]Setting leverage for ETH/USD to 5x:[/bold]")
        result = gmx.set_leverage(5.0, "ETH/USD")
        console.print(f"  {result['info']['message']}")

        # Set leverage for another symbol
        console.print("\n[bold]Setting leverage for BTC/USD to 10x:[/bold]")
        result = gmx.set_leverage(10.0, "BTC/USD")
        console.print(f"  {result['info']['message']}")

        # Set default leverage
        console.print("\n[bold]Setting default leverage to 3x:[/bold]")
        result = gmx.set_leverage(3.0)
        console.print(f"  {result['info']['message']}")

        console.print("\n[dim]Note: Leverage settings are stored locally and will be used for future order creation[/dim]")

    except ValueError as e:
        console.print(f"[yellow]Skipped: {e}[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def example_fetch_leverage(gmx: GMXCCXT):
    """Example:fetch_leverage() - Query leverage configuration"""
    console.print("\n[bold cyan]3. fetch_leverage() - Query Leverage Configuration[/bold cyan]")
    console.print("Fetching current leverage settings...\n")

    try:
        # Get leverage for specific symbol
        console.print("[bold]Getting leverage for ETH/USD:[/bold]")
        leverage_info = gmx.fetch_leverage("ETH/USD")
        console.print(f"  ETH/USD leverage: {leverage_info['leverage']}x")

        console.print("\n[bold]Getting leverage for BTC/USD:[/bold]")
        leverage_info = gmx.fetch_leverage("BTC/USD")
        console.print(f"  BTC/USD leverage: {leverage_info['leverage']}x")

        # Get all leverage settings
        console.print("\n[bold]Getting all leverage settings:[/bold]")
        all_leverage = gmx.fetch_leverage()

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Symbol", style="cyan")
        table.add_column("Leverage", justify="right")

        for lev in all_leverage:
            symbol = lev['symbol']
            leverage = f"{lev['leverage']:.1f}x"
            table.add_row(symbol, leverage)

        console.print(table)

    except ValueError as e:
        console.print(f"[yellow]Skipped: {e}[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def example_margin_methods():
    """Example:margin methods (not implemented)"""
    console.print("\n[bold cyan]4. Margin Methods - Not Yet Implemented[/bold cyan]")
    console.print("add_margin() and reduce_margin() require GMX contract integration...\n")

    console.print("[yellow]These methods will raise NotImplementedError:[/yellow]")
    console.print("  • add_margin(symbol, amount) - Add collateral to position")
    console.print("  • reduce_margin(symbol, amount) - Remove collateral from position")
    console.print("\n[dim]These will be implemented when GMX trading contract methods are added[/dim]")


def main():
    console.print(Panel.fit(
        "[bold cyan]GMX CCXT Position Management Examples[/bold cyan]\n"
        "Position management and leverage methods\n"
        "[yellow]Note: Margin methods require smart contract integration[/yellow]",
        border_style="cyan"
    ))

    # Get wallet address from environment
    wallet_address = os.environ.get("WALLET_ADDRESS")
    if not wallet_address:
        console.print("[red]Error: WALLET_ADDRESS environment variable not set[/red]")
        console.print("Usage: export WALLET_ADDRESS='0xYourAddress'")
        return

    # Initialize GMX CCXT wrapper
    rpc = os.environ.get("JSON_RPC_ARBITRUM")
    if not rpc:
        console.print("[yellow]Warning: JSON_RPC_ARBITRUM not found, using default RPC[/yellow]")
        rpc = "https://arb1.arbitrum.io/rpc"

    console.print(f"\n[dim]Connecting to Arbitrum: {rpc}[/dim]")
    console.print(f"[dim]Wallet Address: {wallet_address}[/dim]")

    try:
        web3 = Web3(Web3.HTTPProvider(rpc))
        config = GMXConfig(web3, user_wallet_address=wallet_address)
        gmx = GMXCCXT(config)

        console.print(f"[dim]Chain ID: {web3.eth.chain_id}[/dim]")
        console.print("[green]✓ Connected successfully[/green]")

        # Run all examples
        example_fetch_positions(gmx)
        example_set_leverage(gmx)
        example_fetch_leverage(gmx)
        example_margin_methods()

        console.print("\n" + "=" * 60)
        console.print("[bold green]✓ All position management methods executed successfully![/bold green]")
        console.print("=" * 60)

    except Exception as e:
        console.print(f"\n[bold red]✗ Error: {e}[/bold red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise


if __name__ == "__main__":
    main()
