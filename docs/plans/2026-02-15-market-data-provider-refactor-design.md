# Market Data Provider Refactor Design

## Background

当前实现的核心是 `FundingRateProvider + CcxtBaseProvider`，主要覆盖永续资金费率。
新目标是在保持资金费能力的同时，引入现货价格能力，并为未来深度数据扩展预留结构。

本次重构采用能力拆分方案：不同数据类型拆成独立接口和独立 ccxt 基类。

## Scope (This Refactor)

- 保留并继续支持资金费率能力
- 新增现货价格能力
- 预留深度能力接口与模型（不在本次实现完整业务）
- 支持交易所能力差异（有的只支持 spot 或 only perp）

不包含：
- 向后兼容迁移层（不做迁移策略，直接改）
- WebSocket 数据流
- 多市场聚合策略逻辑

## Target Architecture

### 1. Interface Layer by Capability

- `FundingRateProvider`
- `SpotPriceProvider`
- `OrderBookProvider`（预留）

并引入 capability 枚举：
- `FUNDING_RATE`
- `SPOT_PRICE`
- `ORDER_BOOK`

### 2. CCXT Base Layer by Data Type

- `CcxtProviderCore`
  - 连接创建/缓存
  - 公共错误映射
  - Decimal 与时间工具
- `CcxtFundingProviderBase`
  - 仅资金费相关 fetch/map
- `CcxtSpotProviderBase`
  - 仅现货 ticker 相关 fetch/map
- `CcxtOrderBookProviderBase`（预留）
  - 仅深度相关 fetch/map

### 3. Exchange Providers via Composition

每个交易所 provider 通过多继承/组合只接入需要的能力：
- 同时支持 funding+spot：继承 `CcxtFundingProviderBase + CcxtSpotProviderBase`
- 仅支持 spot：只继承 `CcxtSpotProviderBase`
- 仅支持 funding：只继承 `CcxtFundingProviderBase`

provider 暴露：
- `exchange_id`
- `capabilities: set[ProviderCapability]`
- 交易所默认 options

### 4. Service Layer

- `MarketDataService.get_provider(exchange)`
- 使用 `provider.supports(capability)` 判断能力
- 调用不支持的能力时抛 `UnsupportedCapabilityError`

## Domain Models

按能力拆分模型：

- `domain/models/funding.py`
  - `FundingRateCurrent`
  - `FundingRateHistoryItem`
- `domain/models/spot.py`
  - `SpotTicker`
- `domain/models/orderbook.py`（预留）
  - `OrderBookSnapshot`
  - `OrderBookLevel`

统一约定：
- 价格/费率使用 `Decimal`
- 时间戳统一毫秒
- 返回标准化字段，不透出交易所私有原始结构

## Domain Errors

保留并扩展统一错误：
- `FundingProviderError`（后续可抽象命名为 `MarketDataProviderError`）
- `FundingNetworkError`
- `FundingRateLimitError`
- `FundingSymbolNotFoundError`
- `FundingDataError`
- `UnsupportedCapabilityError`（新增）

## Testing Strategy

目录按能力拆分：
- `tests/unit/domain/*`
- `tests/unit/providers/funding/*`
- `tests/unit/providers/spot/*`
- `tests/unit/providers/orderbook/*`（预留）
- `tests/unit/service/*`

关键断言：
- capability 声明正确
- 能力不支持时报错正确
- Decimal 精度与毫秒时间一致性
- 交易所 options 符合预期

## Verification Commands

```bash
uv run pytest tests/unit -v
RUN_LIVE_TESTS=1 uv run pytest tests/integration/test_binance_live.py -v
```
