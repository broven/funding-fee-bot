# funding-fee-bot

资金费套利机器人（当前聚焦资金费数据获取层）。

## Current Scope

- Python + ccxt
- 统一资金费接口
- Binance provider（内部基于 `CcxtBaseProvider`）
- 支持：
  - 单交易对当前资金费率
  - 全市场当前资金费率
  - 历史资金费率（`since` / `limit`）

## Quick Start

```bash
python -m pip install -e .
```

## Run Tests

```bash
pytest tests/unit -v
```

可选 live 测试（需要外网和可用交易所 API）：

```bash
RUN_LIVE_TESTS=1 pytest tests/integration/test_binance_live.py -v
```
