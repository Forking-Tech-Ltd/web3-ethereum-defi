"""
Unit tests for GMX Subsquid GraphQL client.

Tests the Subsquid GraphQL client without requiring live network access.
"""

import pytest
from unittest.mock import Mock, patch
from eth_defi.gmx.subsquid import GMXSubsquidClient


@pytest.fixture
def mock_market_infos_response():
    """
    Create mock market info response from Subsquid.

    :returns: Mock GraphQL response with market data
    :rtype: Dict
    """
    return {
        "data": {
            "marketInfos": [
                {
                    "id": "1",
                    "marketTokenAddress": "0x70d95587d40A2caf56bd97485aB3Eec10Bee6336",
                    "indexTokenAddress": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
                    "longTokenAddress": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
                    "shortTokenAddress": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
                    "longOpenInterestUsd": "50000000000000000000000000000000000000",
                    "shortOpenInterestUsd": "45000000000000000000000000000000000000",
                    "longOpenInterestInTokens": "25000000000000000000",
                    "shortOpenInterestInTokens": "22500000000000000000",
                    "fundingFactorPerSecond": "100000000000000000000000000000",
                    "longsPayShorts": True,
                    "borrowingFactorPerSecondForLongs": "50000000000000000000000000000",
                    "borrowingFactorPerSecondForShorts": "45000000000000000000000000000",
                }
            ]
        }
    }


@pytest.fixture
def mock_borrowing_rate_response():
    """
    Create mock borrowing rate response from Subsquid.

    :returns: Mock GraphQL response with borrowing rate data
    :rtype: Dict
    """
    return {
        "data": {
            "borrowingRateSnapshots": [
                {
                    "id": "1",
                    "marketAddress": "0x70d95587d40A2caf56bd97485aB3Eec10Bee6336",
                    "isLong": True,
                    "borrowingRate": "1000000000000000000000000000000",
                    "timestamp": 1704286800,
                }
            ]
        }
    }


@pytest.fixture
def mock_positions_response():
    """
    Create mock positions response from Subsquid.

    :returns: Mock GraphQL response with position data
    :rtype: Dict
    """
    return {
        "data": {
            "positions": [
                {
                    "id": "1",
                    "positionKey": "0xabc123",
                    "account": "0x1234567890123456789012345678901234567890",
                    "market": "0x70d95587d40A2caf56bd97485aB3Eec10Bee6336",
                    "collateralToken": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
                    "isLong": True,
                    "collateralAmount": "1000000000000000000",
                    "sizeInUsd": "5000000000000000000000000000000000000",
                    "sizeInTokens": "2500000000000000000",
                    "entryPrice": "2000000000000000000000000000000000000",
                    "realizedPnl": "0",
                    "unrealizedPnl": "100000000000000000000000000000000000",
                    "realizedFees": "10000000000000000000000000000000000",
                    "unrealizedFees": "5000000000000000000000000000000000",
                    "leverage": "5000000000000000000",
                    "openedAt": 1704286800,
                }
            ]
        }
    }


@pytest.fixture
def mock_markets_response():
    """
    Create mock markets response from Subsquid.

    :returns: Mock GraphQL response with market list
    :rtype: Dict
    """
    return {
        "data": {
            "markets": [
                {
                    "id": "0x70d95587d40A2caf56bd97485aB3Eec10Bee6336",
                    "indexToken": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
                    "longToken": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
                    "shortToken": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
                }
            ]
        }
    }


def test_subsquid_initialization():
    """Test Subsquid client initialization."""
    client = GMXSubsquidClient()
    assert client.endpoint == "https://gmx.squids.live/gmx-synthetics-arbitrum:prod/api/graphql"
    assert client.timeout == 30

    custom_client = GMXSubsquidClient(endpoint="https://custom.endpoint", timeout=60)
    assert custom_client.endpoint == "https://custom.endpoint"
    assert custom_client.timeout == 60


def test_get_market_infos(mock_market_infos_response):
    """Test fetching market infos."""
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = mock_market_infos_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        client = GMXSubsquidClient()
        result = client.get_market_infos(limit=1)

        assert len(result) == 1
        assert result[0]["id"] == "1"
        assert result[0]["longOpenInterestUsd"] == "50000000000000000000000000000000"
        assert result[0]["fundingFactorPerSecond"] == "100000000000000000000000000"


def test_get_market_infos_with_filter(mock_market_infos_response):
    """Test fetching market infos with market address filter."""
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = mock_market_infos_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        client = GMXSubsquidClient()
        result = client.get_market_infos(
            market_address="0x70d95587d40A2caf56bd97485aB3Eec10Bee6336",
            limit=1
        )

        assert len(result) == 1
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        query = call_args[1]["json"]["query"]
        assert 'where: { marketTokenAddress_eq: "0x70d95587d40A2caf56bd97485aB3Eec10Bee6336" }' in query


def test_get_borrowing_rate_snapshots(mock_borrowing_rate_response):
    """Test fetching borrowing rate snapshots."""
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = mock_borrowing_rate_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        client = GMXSubsquidClient()
        result = client.get_borrowing_rate_snapshots(limit=1)

        assert len(result) == 1
        assert result[0]["marketAddress"] == "0x70d95587d40A2caf56bd97485aB3Eec10Bee6336"
        assert result[0]["isLong"] is True
        assert result[0]["borrowingRate"] == "1000000000000000000000000000"


def test_get_borrowing_rate_snapshots_with_filters(mock_borrowing_rate_response):
    """Test fetching borrowing rate snapshots with filters."""
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = mock_borrowing_rate_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        client = GMXSubsquidClient()
        result = client.get_borrowing_rate_snapshots(
            market_address="0x70d95587d40A2caf56bd97485aB3Eec10Bee6336",
            is_long=True,
            since_timestamp=1704286800,
            limit=1
        )

        assert len(result) == 1
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        query = call_args[1]["json"]["query"]
        assert "marketAddress_eq" in query
        assert "isLong_eq" in query
        assert "timestamp_gte" in query


def test_get_positions(mock_positions_response):
    """Test fetching positions."""
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = mock_positions_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        client = GMXSubsquidClient()
        result = client.get_positions(limit=1)

        assert len(result) == 1
        assert result[0]["positionKey"] == "0xabc123"
        assert result[0]["isLong"] is True
        assert result[0]["sizeInUsd"] == "5000000000000000000000000000000"


def test_get_positions_with_filters(mock_positions_response):
    """Test fetching positions with account and market filters."""
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = mock_positions_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        client = GMXSubsquidClient()
        result = client.get_positions(
            account="0x1234567890123456789012345678901234567890",
            market="0x70d95587d40A2caf56bd97485aB3Eec10Bee6336",
            limit=1
        )

        assert len(result) == 1
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        query = call_args[1]["json"]["query"]
        assert "account_eq" in query
        assert "market_eq" in query


def test_get_markets(mock_markets_response):
    """Test fetching markets."""
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = mock_markets_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        client = GMXSubsquidClient()
        result = client.get_markets()

        assert len(result) == 1
        assert result[0]["id"] == "0x70d95587d40A2caf56bd97485aB3Eec10Bee6336"
        assert result[0]["indexToken"] == "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1"


def test_query_error_handling():
    """Test GraphQL error handling."""
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {
            "errors": [{"message": "Invalid query"}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        client = GMXSubsquidClient()
        with pytest.raises(ValueError, match="GraphQL query error"):
            client.query("invalid query")


def test_query_http_error():
    """Test HTTP error handling."""
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 500 Error")
        mock_post.return_value = mock_response

        client = GMXSubsquidClient()
        with pytest.raises(Exception, match="HTTP 500 Error"):
            client.query("query { markets { id } }")
