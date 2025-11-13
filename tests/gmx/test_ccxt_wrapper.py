"""
Unit tests for GMX CCXT-compatible wrapper.

Tests the CCXT-compatible interface for GMX protocol without requiring live network access.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from eth_defi.gmx.ccxt.wrapper import GMXCCXTWrapper


@pytest.fixture
def mock_config():
    """Create a mock GMX config."""
    config = Mock()
    config.get_chain.return_value = "arbitrum"
    return config


@pytest.fixture
def mock_api():
    """Create a mock GMX API."""
    api = Mock()
    # Mock token response
    api.get_tokens.return_value = {
        "tokens": [
            {"symbol": "ETH", "address": "0x123"},
            {"symbol": "BTC", "address": "0x456"},
            {"symbol": "ARB", "address": "0x789"},
        ]
    }
    # Mock candlesticks response (GMX format: 5 fields)
    api.get_candlesticks.return_value = {
        "candles": [
            [1704286800, 2247.9, 2250.0, 2240.0, 2245.5],  # timestamp(s), open, high, low, close
            [1704290400, 2245.5, 2260.0, 2243.0, 2258.3],
            [1704294000, 2258.3, 2265.0, 2255.0, 2262.1],
        ]
    }
    return api


def test_initialization(mock_config):
    """Test CCXT wrapper initialization."""
    with patch("eth_defi.gmx.ccxt.wrapper.GMXAPI"):
        wrapper = GMXCCXTWrapper(mock_config)

        assert wrapper.config == mock_config
        assert wrapper.markets_loaded is False
        assert "1m" in wrapper.timeframes
        assert "1h" in wrapper.timeframes
        assert "1d" in wrapper.timeframes


def test_timeframes(mock_config):
    """Test supported timeframes."""
    with patch("eth_defi.gmx.ccxt.wrapper.GMXAPI"):
        wrapper = GMXCCXTWrapper(mock_config)

        expected_timeframes = ["1m", "5m", "15m", "1h", "4h", "1d"]
        for tf in expected_timeframes:
            assert tf in wrapper.timeframes


def test_parse_ohlcv(mock_config):
    """Test parsing single OHLCV candle from GMX format to CCXT format."""
    with patch("eth_defi.gmx.ccxt.wrapper.GMXAPI"):
        wrapper = GMXCCXTWrapper(mock_config)

        # GMX format: [timestamp_seconds, open, high, low, close]
        gmx_candle = [1704286800, 2247.9, 2250.0, 2240.0, 2245.5]

        # Parse to CCXT format
        parsed = wrapper.parse_ohlcv(gmx_candle)

        # CCXT format: [timestamp_ms, open, high, low, close, volume]
        assert len(parsed) == 6
        assert parsed[0] == 1704286800 * 1000  # Timestamp converted to milliseconds
        assert parsed[1] == 2247.9  # Open
        assert parsed[2] == 2250.0  # High
        assert parsed[3] == 2240.0  # Low
        assert parsed[4] == 2245.5  # Close
        assert parsed[5] is None  # Volume (GMX doesn't provide)


def test_parse_ohlcvs(mock_config):
    """Test parsing multiple OHLCV candles."""
    with patch("eth_defi.gmx.ccxt.wrapper.GMXAPI"):
        wrapper = GMXCCXTWrapper(mock_config)

        gmx_candles = [
            [1704286800, 2247.9, 2250.0, 2240.0, 2245.5],
            [1704290400, 2245.5, 2260.0, 2243.0, 2258.3],
            [1704294000, 2258.3, 2265.0, 2255.0, 2262.1],
        ]

        parsed = wrapper.parse_ohlcvs(gmx_candles)

        assert len(parsed) == 3
        # Check first candle
        assert parsed[0][0] == 1704286800 * 1000
        assert parsed[0][4] == 2245.5
        # Check last candle
        assert parsed[2][0] == 1704294000 * 1000
        assert parsed[2][4] == 2262.1


def test_parse_ohlcvs_with_since(mock_config):
    """Test filtering OHLCV data by 'since' parameter."""
    with patch("eth_defi.gmx.ccxt.wrapper.GMXAPI"):
        wrapper = GMXCCXTWrapper(mock_config)

        gmx_candles = [
            [1704286800, 2247.9, 2250.0, 2240.0, 2245.5],
            [1704290400, 2245.5, 2260.0, 2243.0, 2258.3],
            [1704294000, 2258.3, 2265.0, 2255.0, 2262.1],
        ]

        # Filter to only include candles after second timestamp
        since_ms = 1704290400 * 1000
        parsed = wrapper.parse_ohlcvs(gmx_candles, since=since_ms)

        # Should only include last 2 candles
        assert len(parsed) == 2
        assert parsed[0][0] == 1704290400 * 1000
        assert parsed[1][0] == 1704294000 * 1000


def test_parse_ohlcvs_with_limit(mock_config):
    """Test limiting number of OHLCV candles returned."""
    with patch("eth_defi.gmx.ccxt.wrapper.GMXAPI"):
        wrapper = GMXCCXTWrapper(mock_config)

        gmx_candles = [
            [1704286800, 2247.9, 2250.0, 2240.0, 2245.5],
            [1704290400, 2245.5, 2260.0, 2243.0, 2258.3],
            [1704294000, 2258.3, 2265.0, 2255.0, 2262.1],
        ]

        # Limit to 2 candles (should return last 2 by default)
        parsed = wrapper.parse_ohlcvs(gmx_candles, limit=2, use_tail=True)

        assert len(parsed) == 2
        # Should be the most recent 2 candles
        assert parsed[0][0] == 1704290400 * 1000
        assert parsed[1][0] == 1704294000 * 1000


def test_parse_timeframe(mock_config):
    """Test converting timeframe strings to seconds."""
    with patch("eth_defi.gmx.ccxt.wrapper.GMXAPI"):
        wrapper = GMXCCXTWrapper(mock_config)

        assert wrapper.parse_timeframe("1m") == 60
        assert wrapper.parse_timeframe("5m") == 300
        assert wrapper.parse_timeframe("15m") == 900
        assert wrapper.parse_timeframe("1h") == 3600
        assert wrapper.parse_timeframe("4h") == 14400
        assert wrapper.parse_timeframe("1d") == 86400


def test_parse_timeframe_invalid(mock_config):
    """Test error handling for invalid timeframe."""
    with patch("eth_defi.gmx.ccxt.wrapper.GMXAPI"):
        wrapper = GMXCCXTWrapper(mock_config)

        with pytest.raises(ValueError, match="Invalid timeframe"):
            wrapper.parse_timeframe("invalid")


@pytest.mark.asyncio
async def test_load_markets(mock_config, mock_api):
    """Test loading markets from GMX API."""
    with patch("eth_defi.gmx.ccxt.wrapper.GMXAPI", return_value=mock_api):
        wrapper = GMXCCXTWrapper(mock_config)

        markets = await wrapper.load_markets()

        assert wrapper.markets_loaded is True
        assert len(markets) == 3  # ETH, BTC, ARB
        assert "ETH/USD" in markets
        assert "BTC/USD" in markets
        assert "ARB/USD" in markets

        # Check market structure
        eth_market = markets["ETH/USD"]
        assert eth_market["id"] == "ETH"
        assert eth_market["symbol"] == "ETH/USD"
        assert eth_market["base"] == "ETH"
        assert eth_market["quote"] == "USD"
        assert eth_market["active"] is True


@pytest.mark.asyncio
async def test_load_markets_caching(mock_config, mock_api):
    """Test that markets are cached after first load."""
    with patch("eth_defi.gmx.ccxt.wrapper.GMXAPI", return_value=mock_api):
        wrapper = GMXCCXTWrapper(mock_config)

        # First load
        markets1 = await wrapper.load_markets()
        call_count_1 = mock_api.get_tokens.call_count

        # Second load (should use cache)
        markets2 = await wrapper.load_markets()
        call_count_2 = mock_api.get_tokens.call_count

        assert markets1 == markets2
        assert call_count_1 == call_count_2  # API not called again


@pytest.mark.asyncio
async def test_load_markets_reload(mock_config, mock_api):
    """Test forcing market reload."""
    with patch("eth_defi.gmx.ccxt.wrapper.GMXAPI", return_value=mock_api):
        wrapper = GMXCCXTWrapper(mock_config)

        # First load
        await wrapper.load_markets()
        call_count_1 = mock_api.get_tokens.call_count

        # Force reload
        await wrapper.load_markets(reload=True)
        call_count_2 = mock_api.get_tokens.call_count

        assert call_count_2 > call_count_1  # API called again


@pytest.mark.asyncio
async def test_fetch_ohlcv(mock_config, mock_api):
    """Test fetching OHLCV data."""
    with patch("eth_defi.gmx.ccxt.wrapper.GMXAPI", return_value=mock_api):
        wrapper = GMXCCXTWrapper(mock_config)

        # Load markets first
        await wrapper.load_markets()

        # Fetch OHLCV
        ohlcv = await wrapper.fetch_ohlcv("ETH/USD", "1h", limit=3)

        # Verify API was called correctly
        mock_api.get_candlesticks.assert_called_once_with("ETH", "1h")

        # Verify response format
        assert len(ohlcv) == 3
        assert len(ohlcv[0]) == 6  # CCXT format has 6 fields
        assert ohlcv[0][5] is None  # Volume is None


@pytest.mark.asyncio
async def test_fetch_ohlcv_invalid_symbol(mock_config, mock_api):
    """Test error handling for invalid symbol."""
    with patch("eth_defi.gmx.ccxt.wrapper.GMXAPI", return_value=mock_api):
        wrapper = GMXCCXTWrapper(mock_config)
        await wrapper.load_markets()

        with pytest.raises(ValueError, match="Market .* not found"):
            await wrapper.fetch_ohlcv("INVALID/USD", "1h")


@pytest.mark.asyncio
async def test_fetch_ohlcv_invalid_timeframe(mock_config, mock_api):
    """Test error handling for invalid timeframe."""
    with patch("eth_defi.gmx.ccxt.wrapper.GMXAPI", return_value=mock_api):
        wrapper = GMXCCXTWrapper(mock_config)
        await wrapper.load_markets()

        with pytest.raises(ValueError, match="Invalid timeframe"):
            await wrapper.fetch_ohlcv("ETH/USD", "invalid")


def test_safe_integer(mock_config):
    """Test safe integer extraction."""
    with patch("eth_defi.gmx.ccxt.wrapper.GMXAPI"):
        wrapper = GMXCCXTWrapper(mock_config)

        assert wrapper.safe_integer({"key": 123}, "key") == 123
        assert wrapper.safe_integer({"key": "456"}, "key") == 456
        assert wrapper.safe_integer({}, "key", default=99) == 99
        assert wrapper.safe_integer({"key": None}, "key", default=99) == 99


def test_safe_string(mock_config):
    """Test safe string extraction."""
    with patch("eth_defi.gmx.ccxt.wrapper.GMXAPI"):
        wrapper = GMXCCXTWrapper(mock_config)

        assert wrapper.safe_string({"key": "value"}, "key") == "value"
        assert wrapper.safe_string({"key": 123}, "key") == "123"
        assert wrapper.safe_string({}, "key", default="default") == "default"


def test_omit(mock_config):
    """Test dictionary key omission."""
    with patch("eth_defi.gmx.ccxt.wrapper.GMXAPI"):
        wrapper = GMXCCXTWrapper(mock_config)

        original = {"a": 1, "b": 2, "c": 3}
        result = wrapper.omit(original, ["b"])

        assert "a" in result
        assert "b" not in result
        assert "c" in result
        assert result == {"a": 1, "c": 3}
