#!/usr/bin/env python3
"""
GMX CCXT Phase 2 - Trading Operations Demo

Demonstrates all Phase 2 CCXT-compatible trading/account methods:
- fetch_balance() - Account token balances
- fetch_open_orders() - Open positions as orders
- fetch_my_trades() - User trade history

Note: Trading methods (create_order, cancel_order) require private keys
and are not included in this demo for security reasons.

Usage:
    export WALLET_ADDRESS="0xYourAddress"
    export JSON_RPC_ARBITRUM="https://arb1.arbitrum.io/rpc"
    python scripts/gmx/gmx_ccxt_phase2_demo.py
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


def demo_fetch_balance(gmx: GMXCCXT):
    """Demo fetch_balance() - Account token balances"""
    console.print("\n[bold cyan]1. fetch_balance() - Account Token Balances[/bold cyan]")
    console.print("Fetching wallet balances...\n")

    try:
        balance = gmx.fetch_balance()

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Token", style="cyan")
        table.add_column("Free", justify="right")
        table.add_column("Used", justify="right")
        table.add_column("Total", justify="right")

        # Show tokens with non-zero balance
        shown = 0
        for currency in sorted(balance.keys()):
            if currency in ['free', 'used', 'total', 'info']:
                continue

            amounts = balance[currency]
            total = amounts.get('total', 0)

            if total > 0:
                free = f"{amounts.get('free', 0):.6f}"
                used = f"{amounts.get('used', 0):.6f}"
                total_str = f"{total:.6f}"

                table.add_row(currency, free, used, total_str)
                shown += 1

                if shown >= 10:  # Limit display
                    break

        if shown == 0:
            console.print("[yellow]No token balances found (or all balances are 0)[/yellow]")
        else:
            console.print(table)
            console.print(f"\n[dim]Showing top {shown} tokens with balance[/dim]")

    except ValueError as e:
        console.print(f"[yellow]Skipped: {e}[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def demo_fetch_open_orders(gmx: GMXCCXT):
    """Demo fetch_open_orders() - Open positions as orders"""
    console.print("\n[bold cyan]2. fetch_open_orders() - Open Positions[/bold cyan]")
    console.print("Fetching open positions...\n")

    try:
        orders = gmx.fetch_open_orders()

        if not orders:
            console.print("[yellow]No open positions found[/yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan")
        table.add_column("Symbol")
        table.add_column("Side")
        table.add_column("Amount", justify="right")
        table.add_column("Price", justify="right")
        table.add_column("Cost", justify="right")
        table.add_column("Status")

        for order in orders[:10]:  # Show first 10
            order_id = order['id'][:15] + "..." if len(order['id']) > 15 else order['id']
            symbol = order['symbol']
            side_style = "green" if order['side'] == "buy" else "red"
            side = f"[{side_style}]{order['side'].upper()}[/{side_style}]"
            amount = f"{order['amount']:.4f}" if order['amount'] else "N/A"
            price = f"${order['price']:,.2f}" if order['price'] else "N/A"
            cost = f"${order['cost']:,.2f}" if order['cost'] else "N/A"
            status = order['status']

            table.add_row(order_id, symbol, side, amount, price, cost, status)

        console.print(table)
        console.print(f"\n[dim]Total positions: {len(orders)}[/dim]")

        # Demo filtering by symbol
        if len(orders) > 0:
            first_symbol = orders[0]['symbol']
            console.print(f"\n[bold]Filtering to {first_symbol}:[/bold]")
            filtered = gmx.fetch_open_orders(symbol=first_symbol)
            console.print(f"Found {len(filtered)} positions for {first_symbol}")

    except ValueError as e:
        console.print(f"[yellow]Skipped: {e}[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def demo_fetch_my_trades(gmx: GMXCCXT):
    """Demo fetch_my_trades() - User trade history"""
    console.print("\n[bold cyan]3. fetch_my_trades() - User Trade History[/bold cyan]")
    console.print("Fetching trade history (last 7 days)...\n")

    try:
        # Get trades from last 7 days
        since = int((datetime.now() - timedelta(days=7)).timestamp() * 1000)
        trades = gmx.fetch_my_trades(since=since, limit=20)

        if not trades:
            console.print("[yellow]No trades found in the last 7 days[/yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Time", style="cyan")
        table.add_column("Symbol")
        table.add_column("Side")
        table.add_column("Amount", justify="right")
        table.add_column("Price", justify="right")
        table.add_column("Cost", justify="right")

        for trade in trades[:15]:  # Show first 15
            timestamp = datetime.fromisoformat(trade['datetime'].replace('Z', '+00:00'))
            time_str = timestamp.strftime('%m-%d %H:%M')
            symbol = trade['symbol']
            side_style = "green" if trade['side'] == "buy" else "red"
            side = f"[{side_style}]{trade['side'].upper()}[/{side_style}]"
            amount = f"{trade['amount']:.4f}" if trade['amount'] else "N/A"
            price = f"${trade['price']:,.2f}" if trade['price'] else "N/A"
            cost = f"${trade['cost']:,.2f}" if trade['cost'] else "N/A"

            table.add_row(time_str, symbol, side, amount, price, cost)

        console.print(table)
        console.print(f"\n[dim]Total trades: {len(trades)}[/dim]")

    except ValueError as e:
        console.print(f"[yellow]Skipped: {e}[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def main():
    console.print(Panel.fit(
        "[bold cyan]GMX CCXT Phase 2 - Trading Operations Demo[/bold cyan]\n"
        "Demonstrating account and trading history methods\n"
        "[yellow]Note: Actual trading requires private keys (not shown here)[/yellow]",
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

        # Run all demos
        demo_fetch_balance(gmx)
        demo_fetch_open_orders(gmx)
        demo_fetch_my_trades(gmx)

        console.print("\n" + "=" * 60)
        console.print("[bold green]✓ All Phase 2 methods demonstrated successfully![/bold green]")
        console.print("=" * 60)
        console.print("\n[yellow]Note: Trading methods (create_order, cancel_order) require")
        console.print("private keys and are not shown in this demo for security.[/yellow]")

    except Exception as e:
        console.print(f"\n[bold red]✗ Error: {e}[/bold red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise


if __name__ == "__main__":
    main()
