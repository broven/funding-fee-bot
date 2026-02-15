# Funding Fee Fetcher (Historical)

该文档保留为 funding-only 阶段的历史设计记录。

当前主架构已经升级为能力化数据获取器，请查看：

- `docs/architecture/market-data-provider.md`

历史实现要点：

- 只关注资金费率能力
- 基于 `FundingService + FundingRateProvider`
- 交易所 provider 使用 `CcxtBaseProvider` 单基类
