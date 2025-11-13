"""
CCXT-Compatible Wrapper for GMX Protocol

This module provides a CCXT-compatible synchronous interface for accessing GMX protocol
market data and trading functionality. It allows users familiar with CCXT to
seamlessly integrate GMX into their existing trading systems with minimal code changes.

The wrapper implements the core CCXT methods like `fetch_ohlcv`, `load_markets`, and
provides the same data structures that CCXT users expect, making migration from
centralized exchanges to GMX protocol straightforward.

Example usage::

    from web3 import Web3
    from eth_defi.gmx.config import GMXConfig
    from eth_defi.gmx.ccxt import GMXCCXTWrapper

    # Initialize
    web3 = Web3(Web3.HTTPProvider("https://arb1.arbitrum.io/rpc"))
    config = GMXConfig(web3)
    exchange = GMXCCXTWrapper(config)

    # Fetch OHLCV data (CCXT-style)
    ohlcv = exchange.fetch_ohlcv("ETH/USD", "1h", limit=100)
    # Returns: [[timestamp, open, high, low, close, volume], ...]

.. note::
    GMX protocol does not provide volume data in candlesticks, so volume
    will always be 0 in the returned OHLCV arrays.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import time
from eth_defi.gmx.config import GMXConfig
from eth_defi.gmx.api import GMXAPI
from eth_defi.gmx.core.open_interest import GetOpenInterest
from eth_defi.gmx.core.funding_fee import GetFundingFee


class GMXCCXTWrapper:
    """
    CCXT-compatible wrapper for GMX protocol market data and trading.

    This class provides a familiar CCXT-style interface for interacting with
    GMX protocol, implementing synchronous methods and data structures that match
    CCXT conventions. This allows traders to use GMX with minimal changes to
    existing CCXT-based trading systems.

    :ivar config: GMX configuration object
    :vartype config: GMXConfig
    :ivar api: GMX API client for market data
    :vartype api: GMXAPI
    :ivar markets: Dictionary of available markets (populated by load_markets)
    :vartype markets: Dict[str, Any]
    :ivar timeframes: Supported timeframe intervals
    :vartype timeframes: Dict[str, str]
    :ivar markets_loaded: Flag indicating if markets have been loaded
    :vartype markets_loaded: bool
    """

    def __init__(self, config: GMXConfig):
        """
        Initialize the CCXT wrapper with GMX configuration.

        :param config: GMX configuration object containing network settings and optional wallet information
        :type config: GMXConfig
        """
        self.config = config
        self.api = GMXAPI(config)
        self.markets: Dict[str, Any] = {}
        self.markets_loaded = False

        # Timeframes supported by GMX API
        # Maps CCXT-style timeframe strings to GMX API periods
        self.timeframes = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "1h": "1h",
            "4h": "4h",
            "1d": "1d",
        }

    def load_markets(self, reload: bool = False) -> Dict[str, Any]:
        """
        Load available markets from GMX protocol.

        This method fetches the list of supported tokens from GMX and constructs
        CCXT-compatible market structures. Markets are cached after the first load
        to improve performance.

        :param reload: If True, force reload markets even if already loaded
        :type reload: bool
        :returns: Dictionary mapping unified symbols (e.g., "ETH/USD") to market info
        :rtype: Dict[str, Any]

        Example::

            markets = exchange.load_markets()
            print(markets["ETH/USD"])
            # {'id': 'ETH', 'symbol': 'ETH/USD', 'base': 'ETH', 'quote': 'USD', ...}
        """
        if self.markets_loaded and not reload:
            return self.markets

        # Fetch available tokens from GMX
        tokens_response = self.api.get_tokens()

        # Process tokens into CCXT-style markets
        # GMX tokens are priced in USD
        for token in tokens_response.get("tokens", []):
            symbol_name = token.get("symbol", "")
            if not symbol_name:
                continue

            # Create unified symbol (e.g., ETH/USD)
            unified_symbol = f"{symbol_name}/USD"

            self.markets[unified_symbol] = {
                "id": symbol_name,  # GMX uses simple token symbols
                "symbol": unified_symbol,  # CCXT unified symbol
                "base": symbol_name,  # Base currency (e.g., ETH)
                "quote": "USD",  # Quote currency (always USD for GMX)
                "baseId": symbol_name,
                "quoteId": "USD",
                "active": True,
                "type": "spot",  # GMX provides spot-like pricing
                "spot": True,
                "swap": False,
                "future": False,
                "option": False,
                "contract": False,
                "precision": {
                    "amount": 8,
                    "price": 8,
                },
                "limits": {
                    "amount": {"min": None, "max": None},
                    "price": {"min": None, "max": None},
                    "cost": {"min": None, "max": None},
                },
                "info": token,  # Original token data from GMX
            }

        self.markets_loaded = True
        return self.markets

    def fetch_markets(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Fetch all available markets from GMX protocol.

        This method fetches market data from GMX and returns it as a list of market structures.
        Unlike load_markets(), this method does not cache the results and always fetches fresh data.

        :param params: Additional parameters (not used currently)
        :type params: Optional[Dict[str, Any]]
        :returns: List of market structures
        :rtype: List[Dict[str, Any]]

        Example::

            markets = exchange.fetch_markets()
            for market in markets:
                print(f"{market['symbol']}: {market['base']}/{market['quote']}")
        """
        if params is None:
            params = {}

        tokens_response = self.api.get_tokens()
        markets = []

        for token in tokens_response.get("tokens", []):
            symbol_name = token.get("symbol", "")
            if not symbol_name:
                continue

            unified_symbol = f"{symbol_name}/USD"

            market = {
                "id": symbol_name,
                "symbol": unified_symbol,
                "base": symbol_name,
                "quote": "USD",
                "baseId": symbol_name,
                "quoteId": "USD",
                "active": True,
                "type": "spot",
                "spot": True,
                "swap": False,
                "future": False,
                "option": False,
                "contract": False,
                "precision": {
                    "amount": 8,
                    "price": 8,
                },
                "limits": {
                    "amount": {"min": None, "max": None},
                    "price": {"min": None, "max": None},
                    "cost": {"min": None, "max": None},
                },
                "info": token,
            }
            markets.append(market)

        return markets

    def market(self, symbol: str) -> Dict[str, Any]:
        """
        Get market information for a specific trading pair.

        :param symbol: Unified symbol (e.g., "ETH/USD")
        :type symbol: str
        :returns: Market information dictionary
        :rtype: Dict[str, Any]
        :raises ValueError: If markets haven't been loaded or symbol not found
        """
        if not self.markets_loaded:
            raise ValueError(
                "Markets not loaded. Call load_markets() first."
            )

        if symbol not in self.markets:
            raise ValueError(f"Market {symbol} not found. Available markets: {list(self.markets.keys())}")

        return self.markets[symbol]

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1m",
        since: Optional[int] = None,
        limit: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[List]:
        """
        Fetch historical OHLCV (Open, High, Low, Close, Volume) candlestick data.

        This method follows CCXT conventions for fetching historical market data.
        It returns a list of OHLCV candles where each candle is a list of
        [timestamp, open, high, low, close, volume].

        :param symbol: Unified symbol (e.g., "ETH/USD", "BTC/USD")
        :type symbol: str
        :param timeframe: Candlestick interval - "1m", "5m", "15m", "1h", "4h", "1d"
        :type timeframe: str
        :param since: Unix timestamp in milliseconds for the earliest candle to fetch (Note: GMX API returns recent candles, filtering is done client-side)
        :type since: Optional[int]
        :param limit: Maximum number of candles to return
        :type limit: Optional[int]
        :param params: Additional parameters (e.g., {"until": timestamp_ms})
        :type params: Optional[Dict[str, Any]]
        :returns: List of OHLCV candles, each as [timestamp_ms, open, high, low, close, volume]. Volume is always 0 as GMX API doesn't provide volume data
        :rtype: List[List]
        :raises ValueError: If invalid symbol or timeframe

        Example::

            # Fetch last 100 hourly candles for ETH
            candles = exchange.fetch_ohlcv("ETH/USD", "1h", limit=100)

            # Fetch candles since specific time
            since = int(time.time() * 1000) - 86400000  # 24 hours ago
            candles = exchange.fetch_ohlcv("ETH/USD", "1h", since=since)

            # Each candle: [timestamp, open, high, low, close, volume]
            for candle in candles:
                timestamp, o, h, l, c, v = candle
                print(f"{timestamp}: O:{o} H:{h} L:{l} C:{c} V:{v}")
        """
        if params is None:
            params = {}

        # Ensure markets are loaded
        self.load_markets()

        # Get market info and extract GMX token symbol
        market_info = self.market(symbol)
        token_symbol = market_info["id"]  # GMX token symbol (e.g., "ETH")

        # Validate timeframe
        if timeframe not in self.timeframes:
            raise ValueError(
                f"Invalid timeframe: {timeframe}. Supported: {list(self.timeframes.keys())}"
            )

        gmx_period = self.timeframes[timeframe]

        # Fetch candlestick data from GMX API
        response = self.api.get_candlesticks(token_symbol, gmx_period)

        # Parse the response
        candles_data = response.get("candles", [])

        # Parse OHLCV data
        ohlcv = self.parse_ohlcvs(candles_data, market_info, timeframe, since, limit)

        return ohlcv

    def fetch_open_interest(
        self,
        symbol: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Fetch current open interest for a symbol.

        This method returns the current open interest data for both long and short
        positions on GMX protocol. Open interest represents the total value of all
        outstanding positions.

        :param symbol: Unified symbol (e.g., "ETH/USD", "BTC/USD")
        :type symbol: str
        :param params: Additional parameters (not used currently)
        :type params: Optional[Dict[str, Any]]
        :returns: Dictionary with open interest information::

            {
                'symbol': 'ETH/USD',
                'baseVolume': 0,  # Not provided by GMX
                'quoteVolume': 0,  # Not provided by GMX
                'openInterestAmount': 0,  # Not provided by GMX
                'openInterestValue': 123456789.0,  # Total OI in USD
                'longOpenInterest': 62000000.0,  # Long positions in USD
                'shortOpenInterest': 61456789.0,  # Short positions in USD
                'timestamp': 1234567890000,
                'datetime': '2021-01-01T00:00:00.000Z',
                'info': {...}  # Raw GMX data
            }

        :rtype: Dict[str, Any]
        :raises ValueError: If invalid symbol or markets not loaded

        Example::

            # Get current open interest for ETH
            oi = exchange.fetch_open_interest("ETH/USD")
            print(f"Total OI: ${oi['openInterestValue']:,.0f}")
            print(f"Long OI: ${oi['longOpenInterest']:,.0f}")
            print(f"Short OI: ${oi['shortOpenInterest']:,.0f}")

        .. note::
            GMX provides open interest in USD value only. The openInterestAmount
            field (contracts) is not available and set to 0.
        """
        if params is None:
            params = {}

        # Ensure markets are loaded
        self.load_markets()

        # Get market info
        market_info = self.market(symbol)
        gmx_symbol = market_info["base"]  # e.g., "ETH"

        # Fetch open interest data from GMX
        oi_data = GetOpenInterest(self.config).get_data()

        # Extract long and short OI for this symbol
        long_oi = oi_data.get("long", {}).get(gmx_symbol, 0)
        short_oi = oi_data.get("short", {}).get(gmx_symbol, 0)
        total_oi = long_oi + short_oi

        timestamp = self.milliseconds()

        return {
            "symbol": symbol,
            "baseVolume": 0,  # GMX doesn't provide volume
            "quoteVolume": 0,  # GMX doesn't provide volume
            "openInterestAmount": 0,  # GMX doesn't provide this (contracts)
            "openInterestValue": total_oi,  # Total in USD
            "longOpenInterest": long_oi,  # GMX-specific field
            "shortOpenInterest": short_oi,  # GMX-specific field
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp / 1000).isoformat() + "Z",
            "info": {
                "long": long_oi,
                "short": short_oi,
                "symbol": gmx_symbol,
                "raw": oi_data,
            },
        }

    def fetch_open_interest_history(
        self,
        symbol: str,
        timeframe: str = "1h",
        since: Optional[int] = None,
        limit: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch historical open interest data (NOT SUPPORTED).

        GMX protocol does not provide historical open interest data through its APIs.
        This method is included for CCXT compatibility but will raise NotImplementedError.

        :param symbol: Unified symbol (e.g., "ETH/USD")
        :type symbol: str
        :param timeframe: Time interval (not used)
        :type timeframe: str
        :param since: Start timestamp in milliseconds (not used)
        :type since: Optional[int]
        :param limit: Maximum number of records (not used)
        :type limit: Optional[int]
        :param params: Additional parameters (not used)
        :type params: Optional[Dict[str, Any]]
        :returns: This method always raises NotImplementedError
        :rtype: List[Dict[str, Any]]
        :raises NotImplementedError: Always raised as GMX doesn't support this

        .. note::
            To get current open interest, use fetch_open_interest() instead.
            For historical blockchain data, consider using GMX Subgraph/Subsquid.
        """
        raise NotImplementedError(
            "GMX protocol does not provide historical open interest data through "
            "its REST API. Use fetch_open_interest() for current data, or query "
            "the GMX Subgraph/Subsquid for historical blockchain data."
        )

    def fetch_funding_rate(
        self,
        symbol: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Fetch current funding rate for a symbol.

        This method returns the current funding rate (APR) for both long and short
        positions on GMX protocol. Funding rates represent the cost/reward of holding
        leveraged positions.

        :param symbol: Unified symbol (e.g., "ETH/USD", "BTC/USD")
        :type symbol: str
        :param params: Additional parameters (not used currently)
        :type params: Optional[Dict[str, Any]]
        :returns: Dictionary with funding rate information::

            {
                'symbol': 'ETH/USD',
                'fundingRate': 0.0001,  # Weighted average (as decimal)
                'longFundingRate': 0.00015,  # Long position rate
                'shortFundingRate': -0.00005,  # Short position rate
                'fundingTimestamp': 1234567890000,
                'fundingDatetime': '2021-01-01T00:00:00.000Z',
                'timestamp': 1234567890000,
                'datetime': '2021-01-01T00:00:00.000Z',
                'info': {...}  # Raw GMX data
            }

        :rtype: Dict[str, Any]
        :raises ValueError: If invalid symbol or markets not loaded

        Example::

            # Get current funding rate for BTC
            fr = exchange.fetch_funding_rate("BTC/USD")
            print(f"Long funding: {fr['longFundingRate']:.6f}")
            print(f"Short funding: {fr['shortFundingRate']:.6f}")

            # Positive rate = longs pay shorts
            # Negative rate = shorts pay longs

        .. note::
            GMX returns funding rates as hourly APR (factor per hour).
            Positive values mean longs pay shorts, negative means shorts pay longs.
        """
        if params is None:
            params = {}

        # Ensure markets are loaded
        self.load_markets()

        # Get market info
        market_info = self.market(symbol)
        gmx_symbol = market_info["base"]  # e.g., "ETH"

        # Fetch funding rate data from GMX
        funding_data = GetFundingFee(self.config).get_data()

        # Extract long and short funding rates for this symbol
        long_funding = funding_data.get("long", {}).get(gmx_symbol, 0)
        short_funding = funding_data.get("short", {}).get(gmx_symbol, 0)

        # Calculate weighted average (simple average for now)
        avg_funding = (long_funding + short_funding) / 2

        timestamp = self.milliseconds()

        return {
            "symbol": symbol,
            "fundingRate": avg_funding,  # Average rate
            "longFundingRate": long_funding,  # GMX-specific field
            "shortFundingRate": short_funding,  # GMX-specific field
            "fundingTimestamp": timestamp,
            "fundingDatetime": datetime.fromtimestamp(timestamp / 1000).isoformat() + "Z",
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp / 1000).isoformat() + "Z",
            "info": {
                "long": long_funding,
                "short": short_funding,
                "symbol": gmx_symbol,
                "raw": funding_data,
            },
        }

    def fetch_funding_rate_history(
        self,
        symbol: str,
        since: Optional[int] = None,
        limit: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch historical funding rate data (NOT SUPPORTED).

        GMX protocol does not provide historical funding rate data through its APIs.
        This method is included for CCXT compatibility but will raise NotImplementedError.

        :param symbol: Unified symbol (e.g., "ETH/USD")
        :type symbol: str
        :param since: Start timestamp in milliseconds (not used)
        :type since: Optional[int]
        :param limit: Maximum number of records (not used)
        :type limit: Optional[int]
        :param params: Additional parameters (not used)
        :type params: Optional[Dict[str, Any]]
        :returns: This method always raises NotImplementedError
        :rtype: List[Dict[str, Any]]
        :raises NotImplementedError: Always raised as GMX doesn't support this

        .. note::
            To get current funding rates, use fetch_funding_rate() instead.
            For historical blockchain data, consider using GMX Subgraph/Subsquid.
        """
        raise NotImplementedError(
            "GMX protocol does not provide historical funding rate data through "
            "its REST API. Use fetch_funding_rate() for current data, or query "
            "the GMX Subgraph/Subsquid for historical blockchain data."
        )

    def parse_ohlcvs(
        self,
        ohlcvs: List[List],
        market: Optional[Dict[str, Any]] = None,
        timeframe: str = "1m",
        since: Optional[int] = None,
        limit: Optional[int] = None,
        use_tail: bool = True,
    ) -> List[List]:
        """
        Parse multiple OHLCV candles from GMX format to CCXT format.

        Converts GMX candlestick data (5 fields) to CCXT format (6 fields with volume).
        Applies filtering based on 'since' timestamp and 'limit' parameters.

        :param ohlcvs: List of raw OHLCV data from GMX API
        :type ohlcvs: List[List]
        :param market: Market information dictionary (optional)
        :type market: Optional[Dict[str, Any]]
        :param timeframe: Candlestick interval
        :type timeframe: str
        :param since: Filter candles after this timestamp (ms)
        :type since: Optional[int]
        :param limit: Maximum number of candles to return
        :type limit: Optional[int]
        :param use_tail: If True, return the most recent candles when limiting
        :type use_tail: bool
        :returns: List of parsed OHLCV candles in CCXT format
        :rtype: List[List]
        """
        parsed = [self.parse_ohlcv(ohlcv, market) for ohlcv in ohlcvs]

        # Sort by timestamp (ascending)
        parsed = sorted(parsed, key=lambda x: x[0])

        # Filter by 'since' parameter if provided
        if since is not None:
            parsed = [candle for candle in parsed if candle[0] >= since]

        # Apply limit
        if limit is not None and len(parsed) > limit:
            if use_tail:
                # Return the most recent 'limit' candles
                parsed = parsed[-limit:]
            else:
                # Return the oldest 'limit' candles
                parsed = parsed[:limit]

        return parsed

    def parse_ohlcv(
        self,
        ohlcv: List,
        market: Optional[Dict[str, Any]] = None,
    ) -> List:
        """
        Parse a single OHLCV candle from GMX format to CCXT format.

        GMX returns: [timestamp_seconds, open, high, low, close]
        CCXT expects: [timestamp_ms, open, high, low, close, volume]

        :param ohlcv: Single candle data from GMX [timestamp_s, open, high, low, close]
        :type ohlcv: List
        :param market: Market information dictionary (optional)
        :type market: Optional[Dict[str, Any]]
        :returns: Parsed candle in CCXT format [timestamp_ms, open, high, low, close, volume]. Volume is set to 0 as GMX doesn't provide it
        :rtype: List
        """
        # GMX format: [timestamp (seconds), open, high, low, close]
        # CCXT format: [timestamp (milliseconds), open, high, low, close, volume]

        if len(ohlcv) < 5:
            raise ValueError(f"Invalid OHLCV data: expected at least 5 fields, got {len(ohlcv)}")

        timestamp_seconds = ohlcv[0]
        timestamp_ms = int(timestamp_seconds * 1000)  # Convert to milliseconds

        return [
            timestamp_ms,  # Timestamp in milliseconds
            float(ohlcv[1]),  # Open
            float(ohlcv[2]),  # High
            float(ohlcv[3]),  # Low
            float(ohlcv[4]),  # Close
            0,  # Volume (GMX doesn't provide volume data)
        ]

    def parse_timeframe(self, timeframe: str) -> int:
        """
        Convert timeframe string to duration in seconds.

        :param timeframe: Timeframe string (e.g., "1m", "1h", "1d")
        :type timeframe: str
        :returns: Duration in seconds
        :rtype: int

        Example::

            seconds = exchange.parse_timeframe("1h")  # Returns 3600
            seconds = exchange.parse_timeframe("1d")  # Returns 86400
        """
        timeframe_mapping = {
            "1m": 60,
            "5m": 300,
            "15m": 900,
            "1h": 3600,
            "4h": 14400,
            "1d": 86400,
        }

        if timeframe not in timeframe_mapping:
            raise ValueError(f"Invalid timeframe: {timeframe}")

        return timeframe_mapping[timeframe]

    def milliseconds(self) -> int:
        """
        Get current Unix timestamp in milliseconds.

        :returns: Current timestamp in milliseconds
        :rtype: int

        Example::

            now = exchange.milliseconds()
            print(f"Current time: {now} ms")
        """
        return int(time.time() * 1000)

    def safe_integer(
        self,
        dictionary: Dict[str, Any],
        key: str,
        default: Optional[int] = None,
    ) -> Optional[int]:
        """
        Safely extract an integer value from a dictionary.

        :param dictionary: Dictionary to extract from
        :type dictionary: Dict[str, Any]
        :param key: Key to look up
        :type key: str
        :param default: Default value if key not found
        :type default: Optional[int]
        :returns: Integer value or default
        :rtype: Optional[int]
        """
        value = dictionary.get(key, default)
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def safe_string(
        self,
        dictionary: Dict[str, Any],
        key: str,
        default: Optional[str] = None,
    ) -> Optional[str]:
        """
        Safely extract a string value from a dictionary.

        :param dictionary: Dictionary to extract from
        :type dictionary: Dict[str, Any]
        :param key: Key to look up
        :type key: str
        :param default: Default value if key not found
        :type default: Optional[str]
        :returns: String value or default
        :rtype: Optional[str]
        """
        value = dictionary.get(key, default)
        if value is None:
            return default
        return str(value)

    def sum(self, a: float, b: float) -> float:
        """
        Add two numbers safely.

        :param a: First number
        :type a: float
        :param b: Second number
        :type b: float
        :returns: Sum of a and b
        :rtype: float
        """
        return a + b

    def omit(self, dictionary: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
        """
        Create a new dictionary excluding specified keys.

        :param dictionary: Source dictionary
        :type dictionary: Dict[str, Any]
        :param keys: List of keys to exclude
        :type keys: List[str]
        :returns: New dictionary without the specified keys
        :rtype: Dict[str, Any]
        """
        return {k: v for k, v in dictionary.items() if k not in keys}
