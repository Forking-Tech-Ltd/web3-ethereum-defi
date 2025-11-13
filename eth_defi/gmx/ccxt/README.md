# GMX CCXT-Compatible Interface

This module provides a CCXT-compatible interface for the GMX protocol, allowing developers familiar with CCXT to seamlessly integrate GMX into their existing trading systems with minimal code changes.

## Overview

The CCXT wrapper implements the familiar methods and data structures that CCXT users expect, making migration from centralized exchanges to GMX protocol straightforward and intuitive.

## Features

- **CCXT-Compatible API**: Methods like `fetch_ohlcv`, `load_markets` work exactly as expected
- **Standard Data Format**: Returns OHLCV data in standard CCXT format `[timestamp_ms, open, high, low, close, volume]`
- **Async/Await Support**: Fully async implementation for non-blocking operations
- **Multiple Timeframes**: Supports 1m, 5m, 15m, 1h, 4h, and 1d intervals
- **Unified Symbols**: Uses standard format like "ETH/USD", "BTC/USD"

## Quick Start

```python
import asyncio
from web3 import Web3
from eth_defi.gmx.config import GMXConfig
from eth_defi.gmx.ccxt import GMXCCXTWrapper

async def main():
    # Connect to Arbitrum
    web3 = Web3(Web3.HTTPProvider("https://arb1.arbitrum.io/rpc"))
    config = GMXConfig(web3)

    # Create CCXT-compatible wrapper
    exchange = GMXCCXTWrapper(config)

    # Load markets (just like CCXT)
    await exchange.load_markets()

    # Fetch OHLCV data
    ohlcv = await exchange.fetch_ohlcv("ETH/USD", "1h", limit=100)

    # Process candles
    for candle in ohlcv:
        timestamp, open, high, low, close, volume = candle
        print(f"Timestamp: {timestamp}, Close: ${close}")

asyncio.run(main())
```

## API Reference

### GMXCCXTWrapper

#### `__init__(config: GMXConfig)`

Initialize the CCXT wrapper with GMX configuration.

**Parameters:**
- `config`: GMXConfig instance with network settings

#### `async load_markets(reload: bool = False) -> Dict[str, Any]`

Load available markets from GMX protocol.

**Parameters:**
- `reload`: Force reload markets even if already cached

**Returns:** Dictionary of markets indexed by unified symbol (e.g., "ETH/USD")

**Example:**
```python
markets = await exchange.load_markets()
print(f"Available markets: {list(markets.keys())}")
# Output: ['ETH/USD', 'BTC/USD', 'ARB/USD', ...]
```

#### `async fetch_ohlcv(symbol: str, timeframe: str = '1m', since: Optional[int] = None, limit: Optional[int] = None, params: Optional[Dict] = None) -> List[List]`

Fetch historical OHLCV (candlestick) data.

**Parameters:**
- `symbol`: Unified symbol (e.g., "ETH/USD")
- `timeframe`: Interval - "1m", "5m", "15m", "1h", "4h", "1d"
- `since`: Unix timestamp in milliseconds for earliest candle
- `limit`: Maximum number of candles to return
- `params`: Additional parameters

**Returns:** List of OHLCV candles in format:
```
[
    [timestamp_ms, open, high, low, close, volume],
    [timestamp_ms, open, high, low, close, volume],
    ...
]
```

**Example:**
```python
# Get last 50 hourly candles
candles = await exchange.fetch_ohlcv("BTC/USD", "1h", limit=50)

# Get candles from specific time
import time
since = int((time.time() - 86400) * 1000)  # 24 hours ago
candles = await exchange.fetch_ohlcv("ETH/USD", "1h", since=since)
```

### Helper Methods

#### `parse_timeframe(timeframe: str) -> int`

Convert timeframe string to seconds.

**Example:**
```python
seconds = exchange.parse_timeframe("1h")  # Returns 3600
```

#### `milliseconds() -> int`

Get current Unix timestamp in milliseconds.

**Example:**
```python
now = exchange.milliseconds()
```

## Supported Timeframes

| Timeframe | Description |
|-----------|-------------|
| `1m`      | 1 minute    |
| `5m`      | 5 minutes   |
| `15m`     | 15 minutes  |
| `1h`      | 1 hour      |
| `4h`      | 4 hours     |
| `1d`      | 1 day       |

## Important Notes

### Volume Data

⚠️ **GMX API does not provide volume data in candlesticks.** The volume field in returned OHLCV arrays will always be `None`.

```python
timestamp, open, high, low, close, volume = candle
# volume will always be None
```

### Market Symbols

GMX uses a simplified token symbol system internally (e.g., "ETH", "BTC"), but the CCXT wrapper converts these to unified symbols (e.g., "ETH/USD", "BTC/USD") for consistency with CCXT conventions.

### Data Availability

Historical data availability depends on the GMX API. The API typically returns recent candles, and the `since` parameter is applied as a client-side filter.

## Complete Example

See `scripts/gmx/gmx_ccxt_example.py` for a comprehensive example demonstrating:
- Loading markets
- Fetching OHLCV data
- Working with multiple timeframes
- Using the `since` parameter
- Comparing multiple tokens

Run it with:
```bash
python scripts/gmx/gmx_ccxt_example.py
```

## Comparison with CCXT

### Similar to CCXT

✅ Method names (`fetch_ohlcv`, `load_markets`)
✅ Async/await pattern
✅ Data format `[timestamp_ms, O, H, L, C, V]`
✅ Unified symbols ("ETH/USD")
✅ Helper methods (`parse_timeframe`, `milliseconds`)

### Different from CCXT

❌ No volume data (always `None`)
❌ Limited historical data (API dependent)
❌ Fewer timeframe options (6 vs 14+ in some exchanges)
❌ No order placement methods (read-only wrapper)

## Testing

Run the unit tests:
```bash
pytest tests/gmx/test_ccxt_wrapper.py -v
```

## Migration from CCXT

Migrating from a CCXT-based trading system to GMX is straightforward:

```python
# Before (CCXT with Hyperliquid)
from ccxt.async_support import hyperliquid
exchange = hyperliquid()
await exchange.load_markets()
ohlcv = await exchange.fetch_ohlcv("ETH/USD", "1h", limit=100)

# After (GMX with CCXT wrapper)
from eth_defi.gmx.config import GMXConfig
from eth_defi.gmx.ccxt import GMXCCXTWrapper
config = GMXConfig(web3)  # Requires Web3 connection
exchange = GMXCCXTWrapper(config)
await exchange.load_markets()
ohlcv = await exchange.fetch_ohlcv("ETH/USD", "1h", limit=100)
```

The main difference is initialization - GMX requires a Web3 connection to the blockchain, while CCXT exchanges use API keys.

## Troubleshooting

### "Markets not loaded" Error

Make sure to call `await exchange.load_markets()` before fetching OHLCV data:

```python
exchange = GMXCCXTWrapper(config)
await exchange.load_markets()  # Required!
ohlcv = await exchange.fetch_ohlcv("ETH/USD", "1h")
```

### Invalid Symbol Error

Use unified symbols like "ETH/USD", not raw token symbols like "ETH":

```python
# ❌ Wrong
ohlcv = await exchange.fetch_ohlcv("ETH", "1h")

# ✅ Correct
ohlcv = await exchange.fetch_ohlcv("ETH/USD", "1h")
```

### Invalid Timeframe Error

Only use supported timeframes: 1m, 5m, 15m, 1h, 4h, 1d

```python
# ❌ Wrong
ohlcv = await exchange.fetch_ohlcv("ETH/USD", "30m")  # Not supported

# ✅ Correct
ohlcv = await exchange.fetch_ohlcv("ETH/USD", "15m")  # Supported
```

## License

MIT
