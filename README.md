# funding-fee-bot

资金费套利机器人（当前聚焦市场数据获取层）。

## Current Scope

- Python + ccxt
- 能力化统一接口：
  - 资金费率（Funding）
  - 现货价格（Spot）
  - 深度（Order Book，接口预留）
- Binance / Bybit / Bitget providers
- `MarketDataService` 路由 provider，并支持能力检查

## Quick Start

```bash
uv sync --extra dev
```

## Dependency Management (uv)

- 锁文件：`uv.lock`（需要纳入版本控制）
- 新增运行时依赖：`uv add <package>`
- 新增开发依赖（`dev` extra）：`uv add --optional dev <package>`
- 变更依赖后刷新锁文件：`uv lock`
- 同步本地环境：`uv sync --extra dev`

## Run Tests

```bash
uv run pytest tests/unit -v
```

可选 live 测试（需要外网和可用交易所 API）：

```bash
RUN_LIVE_TESTS=1 uv run pytest tests/integration/test_binance_live.py -v
```
