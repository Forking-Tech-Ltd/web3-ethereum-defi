# GMX CCXT Examples

Examples demonstrating the CCXT-compatible interface for GMX protocol.

## Prerequisites

```bash
poetry install --extras "web3v6 data"
```

## Examples

### Fetch Markets
```bash
python scripts/gmx/example_fetch_markets.py
```
Fetches all available markets without caching.

### Basic OHLCV Data
```bash
python scripts/gmx/example_fetch_ohlcv.py
```
Fetches candlestick data for a single symbol.

### Multiple Timeframes
```bash
python scripts/gmx/example_multiple_timeframes.py
```
Compares price data across different timeframes.

### Historical Data
```bash
python scripts/gmx/example_historical_data.py
```
Uses the 'since' parameter to fetch data from a specific timestamp.

### Token Comparison
```bash
python scripts/gmx/example_compare_tokens.py
```
Fetches data for multiple symbols and calculates price correlations.

### Open Interest
```bash
python scripts/gmx/example_open_interest.py
```
Retrieves current open interest with long/short breakdown.

### Funding Rates
```bash
python scripts/gmx/example_funding_rates.py
```
Fetches current funding rates and projects to daily/annual rates.

### Historical Open Interest
```bash
python scripts/gmx/example_historical_open_interest.py
```
Retrieves historical open interest snapshots from Subsquid GraphQL endpoint.

### Historical Funding Rates
```bash
python scripts/gmx/example_historical_funding_rates.py
```
Fetches historical funding rate data from Subsquid GraphQL endpoint.

## Notes

- All examples connect to Arbitrum mainnet RPC
- No wallet or private key required (read-only operations)
- Volume data is always 0 (GMX API limitation)
- Historical data examples use GMX Subsquid GraphQL indexer
