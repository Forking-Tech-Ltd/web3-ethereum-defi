# GMX Squid GraphQL API Reference

GMX Synthetics Arbitrum GraphQL endpoint for querying historical blockchain data.

**Endpoint:** `https://gmx.squids.live/gmx-synthetics-arbitrum:prod/api/graphql`

## Available Query Types

### Platform & Account Statistics
- `platformStats` - Platform-wide statistics
- `accountStats` - Individual account trading statistics
- `periodAccountStats` - Account stats aggregated by period
- `accountPnlHistoryStats` - Historical PnL for accounts
- `accountPnlSummaryStats` - Summary PnL statistics

### Positions
- `positions` - All positions (open and closed)
- `positionById` - Get specific position by ID
- `positionsConnection` - Paginated positions
- `positionChanges` - Historical position changes (increase/decrease)
- `positionsVolume` - Position volume data
- `positionTotalCollateralAmount` - Total collateral metrics

### Markets
- `markets` - Available trading markets
- `marketInfos` - Detailed market information including:
  - Open interest (long/short)
  - Pool amounts and limits
  - Borrowing rates
  - Funding rates
  - Fee factors
  - Price impact factors
  - Virtual pools and inventory
- `marketsAprByPeriod` - APR data by time period
- `marketsPnlAprByPeriod` - PnL-based APR by period

### Orders
- `orders` - All orders (pending/executed/cancelled)
- `orderById` - Get specific order
- `ordersConnection` - Paginated orders
- Order fields include:
  - Order type (market, limit, stop loss, take profit, etc.)
  - Size and collateral amounts
  - Trigger/acceptable prices
  - Status and cancellation reasons
  - Execution details

### Prices
- `prices` - Historical price data
- `priceById` - Specific price point
- `pricesConnection` - Paginated price history

### Trading Actions
- `tradeActions` - All trading actions (deposits, withdrawals, swaps, position changes)
- `transactions` - On-chain transactions
- `swapInfos` - Swap transaction details

### Fees & Collections
- `collectedFeesInfos` - Fees collected by the protocol
- `positionFeesEntities` - Position-specific fees
- `claimActions` - Fee claim actions
- `claimableCollaterals` - Claimable collateral amounts
- `claimableFundingFeeInfos` - Claimable funding fees
- `claimRefs` - Claim references

### Historical Snapshots
- `borrowingRateSnapshots` - Historical borrowing rate data
- `aprSnapshots` - Historical APR snapshots
- `pnlAprSnapshots` - Historical PnL-based APR
- `cumulativePnls` - Cumulative PnL over time
- `cumulativePoolValues` - Historical pool value data
- `performanceSnapshots` - Performance metrics snapshots
- `annualizedPerformance` - Annualized performance data

### GLV (GMX Liquidity Vault)
- `glvs` - GLV vault information
- `glvsAprByPeriod` - GLV APR by period
- `glvsPnlAprByPeriod` - GLV PnL-based APR

### Protocol Configuration
- `onChainSettings` - On-chain protocol settings
- `distributions` - Token distributions
- `claimableAmounts` - Claimable token amounts

### Multichain
- `multichainFundingSendEvents` - Cross-chain funding sent
- `multichainFundingReceiveEvents` - Cross-chain funding received
- `multichainMetadata` - Multichain configuration
- `multichainFunding` - Multichain funding data

### System
- `processorStatuses` - Data processor status
- `squidStatus` - Squid indexer status

## Key Data Entities

### Position
```
- positionKey: Unique position identifier
- account: User wallet address
- market: Market address
- collateralToken: Collateral token address
- isLong: Long (true) or Short (false)
- collateralAmount: Collateral in wei
- sizeInTokens: Position size in tokens
- sizeInUsd: Position size in USD (30 decimals)
- realizedPnl: Realized profit/loss
- unrealizedPnl: Current unrealized profit/loss
- entryPrice: Average entry price
- leverage: Current leverage ratio
- realizedFees: Fees paid
- unrealizedFees: Pending fees
- openedAt: Timestamp when opened
```

### PositionChange
```
- type: INCREASE | DECREASE | LIQUIDATION
- account: Trader address
- market: Market address
- collateralToken: Collateral token
- isLong: Position direction
- sizeInUsd: Total position size
- sizeDeltaUsd: Size change amount
- collateralAmount: Collateral amount
- collateralDeltaAmount: Collateral change
- executionPrice: Execution price
- priceImpactUsd: Price impact in USD
- basePnlUsd: Base PnL
- feesAmount: Fees paid
- timestamp: Block timestamp
```

### MarketInfo
```
- marketTokenAddress: Market token address
- indexTokenAddress: Index token (e.g., ETH, BTC)
- longTokenAddress: Long collateral token
- shortTokenAddress: Short collateral token
- longOpenInterestUsd: Total long OI in USD
- shortOpenInterestUsd: Total short OI in USD
- longOpenInterestInTokens: Long OI in tokens
- shortOpenInterestInTokens: Short OI in tokens
- poolValueMax/Min: Pool valuation bounds
- borrowingFactorPerSecondForLongs: Borrowing rate for longs
- borrowingFactorPerSecondForShorts: Borrowing rate for shorts
- fundingFactorPerSecond: Funding rate per second
- longsPayShorts: Funding direction
- maxOpenInterestLong/Short: OI limits
```

### Order
```
- account: Trader address
- marketAddress: Target market
- orderType: Market, Limit, StopLoss, TakeProfit, etc.
- sizeDeltaUsd: Order size in USD
- initialCollateralDeltaAmount: Collateral amount
- triggerPrice: Trigger price for limit orders
- acceptablePrice: Acceptable execution price
- isLong: Long or short
- status: Pending, Executed, Cancelled, Frozen
- createdTxn: Creation transaction
- executedTxn: Execution transaction
```

## Data Availability

### Historical Open Interest
✅ **Available** via `marketInfos` query
- Query historical snapshots of open interest
- Long and short OI separately
- Token and USD denominated values

### Historical Funding Rates
✅ **Available** via `marketInfos` query
- `fundingFactorPerSecond` - Current funding rate
- `longsPayShorts` - Funding direction
- Can track historical changes through snapshots

### Historical Borrowing Rates
✅ **Available** via `borrowingRateSnapshots` query
- Historical borrowing rate data
- Separated by long and short positions

### Historical Prices
✅ **Available** via `prices` query
- On-chain price data
- Min and max prices
- Token-specific pricing

### Position History
✅ **Available** via:
- `positions` - All positions
- `positionChanges` - Detailed change history
- Complete position lifecycle tracking

### Order History
✅ **Available** via `orders` query
- All order states (pending, executed, cancelled)
- Full order parameters
- Execution details

### Fee History
✅ **Available** via:
- `collectedFeesInfos` - Protocol fees
- `positionFeesEntities` - Position-specific fees
- Historical fee collection data

### Trading Volume
✅ **Available** via:
- `positionsVolume` - Position volume
- `tradeActions` - Individual trades
- Aggregated volume metrics

## Example Queries

### Get Recent Positions
```graphql
query {
  positions(
    orderBy: [openedAt_DESC]
    limit: 10
    where: { account_eq: "0x..." }
  ) {
    id
    account
    market
    isLong
    sizeInUsd
    collateralAmount
    entryPrice
    unrealizedPnl
    openedAt
  }
}
```

### Get Market Open Interest History
```graphql
query {
  marketInfos(
    where: { marketTokenAddress_eq: "0x..." }
    orderBy: [id_DESC]
    limit: 100
  ) {
    id
    longOpenInterestUsd
    shortOpenInterestUsd
    fundingFactorPerSecond
    borrowingFactorPerSecondForLongs
    borrowingFactorPerSecondForShorts
  }
}
```

### Get Position Changes for Analysis
```graphql
query {
  positionChanges(
    where: {
      market_eq: "0x..."
      timestamp_gte: 1700000000
    }
    orderBy: [timestamp_DESC]
    limit: 1000
  ) {
    type
    account
    isLong
    sizeDeltaUsd
    executionPrice
    priceImpactUsd
    basePnlUsd
    feesAmount
    timestamp
  }
}
```

### Get Borrowing Rate History
```graphql
query {
  borrowingRateSnapshots(
    where: { marketAddress_eq: "0x..." }
    orderBy: [timestamp_DESC]
    limit: 100
  ) {
    marketAddress
    isLong
    borrowingRate
    timestamp
  }
}
```

## Notes

- All USD values are in 30 decimals (divide by 1e30)
- All token amounts are in wei (18 decimals for most tokens)
- Timestamps are Unix timestamps in seconds
- Use `Connection` queries for pagination
- Historical data is comprehensive and includes all on-chain events
- Data is indexed from Arbitrum blockchain
