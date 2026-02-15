# Market Data Provider Architecture

## 1. Goal

统一交易所数据获取接口，当前覆盖：

- 资金费率（Perp Funding）
- 现货价格（Spot Ticker）
- 深度能力预留（Order Book）

## 2. Capability-Based Design

核心能力定义：

- `ProviderCapability.FUNDING_RATE`
- `ProviderCapability.SPOT_PRICE`
- `ProviderCapability.ORDER_BOOK`

provider 通过 `capabilities` 声明支持能力，并通过 `supports(capability)` 供上层校验。

## 3. Domain Layer

- `src/funding_fee_bot/domain/interfaces.py`
  - `FundingRateProvider`
  - `SpotPriceProvider`
  - `OrderBookProvider`（预留）
  - `CapabilityAwareProvider`
- `src/funding_fee_bot/domain/models/`
  - `funding.py`：`FundingRateCurrent`, `FundingRateHistoryItem`
  - `spot.py`：`SpotTicker`
  - `orderbook.py`：`OrderBookLevel`, `OrderBookSnapshot`（预留）
- `src/funding_fee_bot/domain/errors.py`
  - 统一 provider 错误
  - `UnsupportedCapabilityError`

## 4. Provider Layer

ccxt 基类按数据类型拆分：

- `CcxtProviderCore`
- `CcxtFundingProviderBase`
- `CcxtSpotProviderBase`
- `CcxtOrderBookProviderBase`（预留）

交易所实现：

- `BinanceMarketDataProvider`
- `BybitMarketDataProvider`
- `BitgetMarketDataProvider`

每个交易所 provider 可以按需组合 funding/spot/orderbook 基类。

## 5. Service Layer

- `MarketDataService.get_provider(exchange, required_capability=None)`
  - 负责路由交易所 provider
  - 可按能力进行 guard
  - 能力不支持时抛 `UnsupportedCapabilityError`

## 6. Extension Rules

新增交易所：

1. 新建 `src/funding_fee_bot/providers/<exchange>.py`
2. 组合所需 base provider（funding/spot/orderbook）
3. 声明 `exchange_id` 和 `capabilities`
4. 注册到 `MarketDataService`
5. 添加 unit tests（provider + service）

## 7. Verification

```bash
uv run pytest tests/unit -v
RUN_LIVE_TESTS=1 uv run pytest tests/integration/test_binance_live.py -v
```
