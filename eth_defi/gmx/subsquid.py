"""
GMX Subsquid GraphQL Client

Client for querying historical GMX data from the Subsquid GraphQL endpoint.
Provides access to historical open interest, funding rates, positions, and other market data.
"""

from typing import Optional, List, Dict, Any
import requests
from datetime import datetime


class GMXSubsquidClient:
    """
    GraphQL client for GMX Subsquid endpoint.

    Provides methods to query historical blockchain data for GMX protocol
    including open interest, funding rates, positions, and market information.

    :ivar endpoint: GraphQL endpoint URL
    :vartype endpoint: str
    :ivar timeout: Request timeout in seconds
    :vartype timeout: int
    """

    def __init__(
        self,
        endpoint: str = "https://gmx.squids.live/gmx-synthetics-arbitrum:prod/api/graphql",
        timeout: int = 30,
    ):
        """
        Initialize the Subsquid GraphQL client.

        :param endpoint: GraphQL endpoint URL
        :type endpoint: str
        :param timeout: Request timeout in seconds
        :type timeout: int
        """
        self.endpoint = endpoint
        self.timeout = timeout

    def query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a GraphQL query.

        :param query: GraphQL query string
        :type query: str
        :param variables: Query variables
        :type variables: Optional[Dict[str, Any]]
        :returns: Query response data
        :rtype: Dict[str, Any]
        :raises requests.exceptions.RequestException: If request fails
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        response = requests.post(
            self.endpoint,
            json=payload,
            timeout=self.timeout,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()

        result = response.json()
        if "errors" in result:
            raise ValueError(f"GraphQL query error: {result['errors']}")

        return result.get("data", {})

    def get_market_infos(
        self,
        market_address: Optional[str] = None,
        limit: int = 100,
        order_by: str = "id_DESC",
    ) -> List[Dict[str, Any]]:
        """
        Get market information snapshots.

        Retrieves historical market data including open interest, funding rates,
        and borrowing rates.

        :param market_address: Filter by specific market address
        :type market_address: Optional[str]
        :param limit: Maximum number of records to return
        :type limit: int
        :param order_by: Sort order (e.g., "id_DESC")
        :type order_by: str
        :returns: List of market info snapshots
        :rtype: List[Dict[str, Any]]
        """
        where_clause = ""
        if market_address:
            where_clause = f'where: {{ marketTokenAddress_eq: "{market_address}" }}'

        query = f"""
        query {{
          marketInfos(
            {where_clause}
            orderBy: [{order_by}]
            limit: {limit}
          ) {{
            id
            marketTokenAddress
            indexTokenAddress
            longTokenAddress
            shortTokenAddress
            longOpenInterestUsd
            shortOpenInterestUsd
            longOpenInterestInTokens
            shortOpenInterestInTokens
            fundingFactorPerSecond
            longsPayShorts
            borrowingFactorPerSecondForLongs
            borrowingFactorPerSecondForShorts
          }}
        }}
        """

        result = self.query(query)
        return result.get("marketInfos", [])

    def get_borrowing_rate_snapshots(
        self,
        market_address: Optional[str] = None,
        is_long: Optional[bool] = None,
        since_timestamp: Optional[int] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get historical borrowing rate snapshots.

        :param market_address: Filter by market address
        :type market_address: Optional[str]
        :param is_long: Filter by long (True) or short (False) positions
        :type is_long: Optional[bool]
        :param since_timestamp: Filter records after this timestamp (seconds)
        :type since_timestamp: Optional[int]
        :param limit: Maximum number of records
        :type limit: int
        :returns: List of borrowing rate snapshots
        :rtype: List[Dict[str, Any]]
        """
        where_conditions = []
        if market_address:
            where_conditions.append(f'marketAddress_eq: "{market_address}"')
        if is_long is not None:
            where_conditions.append(f'isLong_eq: {str(is_long).lower()}')
        if since_timestamp:
            where_conditions.append(f'timestamp_gte: {since_timestamp}')

        where_clause = ""
        if where_conditions:
            where_clause = f'where: {{ {", ".join(where_conditions)} }}'

        query = f"""
        query {{
          borrowingRateSnapshots(
            {where_clause}
            orderBy: [timestamp_DESC]
            limit: {limit}
          ) {{
            id
            marketAddress
            isLong
            borrowingRate
            timestamp
          }}
        }}
        """

        result = self.query(query)
        return result.get("borrowingRateSnapshots", [])

    def get_positions(
        self,
        account: Optional[str] = None,
        market: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get positions.

        :param account: Filter by account address
        :type account: Optional[str]
        :param market: Filter by market address
        :type market: Optional[str]
        :param limit: Maximum number of records
        :type limit: int
        :returns: List of positions
        :rtype: List[Dict[str, Any]]
        """
        where_conditions = []
        if account:
            where_conditions.append(f'account_eq: "{account}"')
        if market:
            where_conditions.append(f'market_eq: "{market}"')

        where_clause = ""
        if where_conditions:
            where_clause = f'where: {{ {", ".join(where_conditions)} }}'

        query = f"""
        query {{
          positions(
            {where_clause}
            orderBy: [openedAt_DESC]
            limit: {limit}
          ) {{
            id
            positionKey
            account
            market
            collateralToken
            isLong
            collateralAmount
            sizeInUsd
            sizeInTokens
            entryPrice
            realizedPnl
            unrealizedPnl
            realizedFees
            unrealizedFees
            leverage
            openedAt
          }}
        }}
        """

        result = self.query(query)
        return result.get("positions", [])

    def get_markets(self) -> List[Dict[str, Any]]:
        """
        Get all available markets.

        :returns: List of markets
        :rtype: List[Dict[str, Any]]
        """
        query = """
        query {
          markets {
            id
            indexToken
            longToken
            shortToken
          }
        }
        """

        result = self.query(query)
        return result.get("markets", [])
