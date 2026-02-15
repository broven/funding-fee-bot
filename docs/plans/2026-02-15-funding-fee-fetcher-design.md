# Funding Fee Fetcher Design

## Background

目标是先落地资金费率数据获取器（Python + ccxt），提供统一接口定义并先支持 Binance USDT-M。
该设计约束：
- 对外接口命名和参数风格尽量贴近 ccxt
- provider 按交易所命名，上层不感知底层框架（ccxt）
- 内部当前优先使用 ccxt 实现
- 第一版同时支持：当前资金费率（单交易对 + 全市场）与历史资金费率

## Scope (V1)

- 交易所：仅 Binance USDT-M
- 查询能力：
  - 单交易对当前资金费率
  - 全市场当前资金费率
  - 单交易对历史资金费率（支持 since/limit）
- 结果：仅返回标准化核心字段（不暴露 raw/info）

## Architecture

### Layering

- `domain/interfaces.py`
  - 定义统一抽象 `FundingRateProvider`
- `domain/models.py`
  - 定义标准化数据模型
- `domain/errors.py`
  - 定义统一异常层
- `providers/ccxt_base_provider.py`
  - `CcxtBaseProvider`：实现 ccxt 通用逻辑（请求、映射、异常转换）
- `providers/binance.py`
  - `BinanceFundingProvider(CcxtBaseProvider)`：仅设置 `exchange_id` 及少量交易所参数
- `service/funding_service.py`（可选）
  - 按 exchange 路由 provider，隔离调用方与 provider 实现

### Extensibility Strategy

- 若后续 Bybit/OKX 也使用 ccxt：
  - 新增 `providers/bybit.py` 或 `providers/okx.py`
  - 继承 `CcxtBaseProvider`
  - 设置 `exchange_id` 与必要选项即可
- 若未来某交易所需直连 REST：
  - 保持同一 `FundingRateProvider` 抽象
  - 新 provider 独立实现，不影响上层

## Unified API Contract

接口命名和参数语义贴近 ccxt：

- `fetch_current(symbol: str) -> FundingRateCurrent`
- `fetch_current_all() -> list[FundingRateCurrent]`
- `fetch_history(symbol: str, since: int | None = None, limit: int | None = None) -> list[FundingRateHistoryItem]`

说明：
- `symbol` 采用 ccxt symbol 形式（例如 `BTC/USDT:USDT`）
- `since` 使用毫秒时间戳
- `limit` 直接透传给 ccxt 的语义

## Data Model

### FundingRateCurrent

- `exchange: str`
- `symbol: str`
- `funding_rate: Decimal`
- `funding_timestamp: int | None`
- `next_funding_timestamp: int | None`
- `fetched_at: int`

### FundingRateHistoryItem

- `exchange: str`
- `symbol: str`
- `funding_rate: Decimal`
- `funding_timestamp: int`
- `fetched_at: int`

约定：
- 所有时间戳统一为毫秒
- `funding_rate` 使用 `Decimal` 避免浮点误差
- 输出只包含标准化字段

## Error Handling

统一异常体系：

- `FundingProviderError`（基类）
- `FundingNetworkError`
- `FundingRateLimitError`
- `FundingSymbolNotFoundError`
- `FundingDataError`

异常元信息：
- `exchange`
- `operation`
- `symbol`（可选）
- `retryable: bool`

映射原则：
- provider 内部将 ccxt 异常转换为统一异常
- 上层仅依赖统一异常，不依赖 ccxt 异常类型

## Testing Strategy (TDD)

- 单元测试优先，全部 mock ccxt 网络调用
- 集成测试可选并默认跳过（手动开启）
- 重点覆盖：
  - 字段标准化
  - 时间戳单位
  - Decimal 精度
  - 异常映射与 `retryable`

建议目录：
- `tests/unit/domain/*`
- `tests/unit/providers/test_binance.py`
- `tests/integration/test_binance_live.py`

## Non-Goals (V1)

- 多交易所并发聚合
- websocket 推流
- 缓存/持久化
- 策略与交易执行模块
