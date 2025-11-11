# GMX Position Leverage Calculation Fix

## Problem

The leverage calculation in `eth_defi/gmx/core/open_positions.py` was incorrect for positions using non-USD collateral (e.g., ETH, WBTC).

### Incorrect Formula (Before)
```python
leverage = position_size_usd / collateral_amount_tokens
```

This formula only works when the collateral token is worth exactly $1 (like USDC). For ETH collateral at $3,450, this would calculate:
```
leverage = $10 / 0.001 ETH = 10,000 (WRONG!)
```

### Correct Formula (After)
```python
leverage = position_size_usd / (collateral_amount_tokens * collateral_price)
```

For the same example:
```
leverage = $10 / (0.001 ETH * $3,450) = $10 / $3.45 = 2.9x (CORRECT)
```

## Changes Made

### 1. Fetch Collateral Token Price from Oracle
- Added logic to fetch oracle prices for **both** index token (for mark price) and collateral token (for leverage calculation)
- Added fallback logic:
  - If collateral token = index token (e.g., ETH position with ETH collateral), use mark price
  - If collateral price unavailable, assume $1 (stablecoin fallback)

### 2. Correct Leverage Calculation
```python
position_size_usd = raw_position[1][0] / 10**30
collateral_amount_tokens = raw_position[1][2] / 10**collateral_token_decimals
collateral_amount_usd = collateral_amount_tokens * collateral_price

if collateral_amount_usd > 0:
    leverage = position_size_usd / collateral_amount_usd
else:
    leverage = 0
```

### 3. Fixed `initial_collateral_amount_usd` Field
This field was incorrectly named - it contained the token amount, not the USD value. Now it correctly contains:
```python
"initial_collateral_amount_usd": collateral_amount_usd
```

## Example from Foundry Tests

From `test/GmxOrderFlow.t.sol`:
```solidity
uint256 constant ETH_PRICE_USD = 3892;  // $3,892 per ETH
uint256 constant ETH_COLLATERAL = 0.001 ether;  // 0.001 ETH collateral
uint256 leverage = 2.5e30;  // 2.5x leverage

// Position size = collateral * price * leverage
uint256 positionSizeUsd = (ETH_COLLATERAL * ETH_PRICE_USD * leverage) / 1e18;
// = (0.001 * 3892 * 2.5) = ~$9.73
```

This matches the correct formula:
```
leverage = position_size / (collateral_amount * collateral_price)
         = $9.73 / (0.001 * $3,892)
         = $9.73 / $3.892
         = 2.5x ✓
```

## Impact

### Before Fix
- ✗ Leverage calculations were **wildly incorrect** for ETH/WBTC collateral positions
- ✗ Would show leverage of 10,000x instead of 2.5x
- ✗ PnL calculations were also affected (they multiply by leverage)

### After Fix
- ✓ Leverage correctly calculated for all collateral types (ETH, WBTC, USDC, etc.)
- ✓ PnL calculations now accurate
- ✓ Tests can properly verify position parameters

## Testing

The fix enables the following tests to pass:
- `tests/gmx/test_trading.py::test_open_long_position`
- `tests/gmx/test_trading.py::test_open_short_position`
- `tests/gmx/test_trading.py::test_open_and_close_position`

These tests:
1. Open positions with ETH collateral at 2.5x leverage
2. Execute orders using mock oracle (ETH=$3,450)
3. Verify position parameters including leverage
4. Close positions and verify cleanup
