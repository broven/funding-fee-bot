# Market Data Provider Refactor Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor the current funding-only provider design into capability-based market data providers that support funding and spot now, while reserving clean extension points for order book data.

**Architecture:** Split abstractions by data capability (`funding`, `spot`, `orderbook`) and split ccxt base classes by data type. Exchange providers compose only required capabilities and expose `capabilities` metadata. `MarketDataService` routes providers and enforces capability checks.

**Tech Stack:** Python 3.10+, `ccxt`, `uv`, `pytest`, `decimal`, dataclasses/typing

---

### Task 1: Add Capability Enum and Capability-Oriented Interfaces

**Files:**
- Create: `src/funding_fee_bot/domain/capabilities.py`
- Modify: `src/funding_fee_bot/domain/interfaces.py`
- Modify: `src/funding_fee_bot/domain/__init__.py`
- Test: `tests/unit/domain/test_capabilities.py`
- Test: `tests/unit/domain/test_interfaces.py`

**Step 1: Write the failing test**

```python
# tests/unit/domain/test_capabilities.py
from funding_fee_bot.domain.capabilities import ProviderCapability


def test_capabilities_enum_contains_expected_values():
    assert ProviderCapability.FUNDING_RATE.value == "funding_rate"
    assert ProviderCapability.SPOT_PRICE.value == "spot_price"
    assert ProviderCapability.ORDER_BOOK.value == "order_book"
```

```python
# tests/unit/domain/test_interfaces.py
from funding_fee_bot.domain.interfaces import SpotPriceProvider, OrderBookProvider


def test_new_interfaces_exist():
    assert hasattr(SpotPriceProvider, "fetch_spot_ticker")
    assert hasattr(OrderBookProvider, "fetch_order_book")
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/domain/test_capabilities.py tests/unit/domain/test_interfaces.py -v`
Expected: FAIL with missing imports/types

**Step 3: Write minimal implementation**

- Add `ProviderCapability` enum.
- Extend interfaces module with:
  - `CapabilityAwareProvider` (or base mixin with `capabilities` + `supports()`)
  - `SpotPriceProvider`
  - `OrderBookProvider` (placeholder contract)
- Keep existing `FundingRateProvider` intact.

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/domain/test_capabilities.py tests/unit/domain/test_interfaces.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/funding_fee_bot/domain/capabilities.py src/funding_fee_bot/domain/interfaces.py src/funding_fee_bot/domain/__init__.py tests/unit/domain/test_capabilities.py tests/unit/domain/test_interfaces.py
git commit -m "feat: add provider capabilities and market data interfaces"
```

### Task 2: Split Domain Models by Data Type

**Files:**
- Create: `src/funding_fee_bot/domain/models/__init__.py`
- Create: `src/funding_fee_bot/domain/models/funding.py`
- Create: `src/funding_fee_bot/domain/models/spot.py`
- Create: `src/funding_fee_bot/domain/models/orderbook.py`
- Modify: `src/funding_fee_bot/domain/__init__.py`
- Test: `tests/unit/domain/test_models_funding.py`
- Test: `tests/unit/domain/test_models_spot.py`
- Test: `tests/unit/domain/test_models_orderbook.py`

**Step 1: Write the failing test**

```python
# tests/unit/domain/test_models_spot.py
from decimal import Decimal
from funding_fee_bot.domain.models.spot import SpotTicker


def test_spot_ticker_model_shape():
    s = SpotTicker(
        exchange="binance",
        symbol="BTC/USDT",
        last=Decimal("60000"),
        bid=Decimal("59999"),
        ask=Decimal("60001"),
        timestamp=1700000000000,
        fetched_at=1700000000123,
    )
    assert s.symbol == "BTC/USDT"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/domain/test_models_spot.py -v`
Expected: FAIL missing module/model

**Step 3: Write minimal implementation**

- Move existing funding models to `models/funding.py`.
- Add `SpotTicker` in `models/spot.py`.
- Add placeholder `OrderBookLevel` and `OrderBookSnapshot` in `models/orderbook.py`.
- Keep stable exports in `models/__init__.py` and `domain/__init__.py`.

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/domain/test_models_funding.py tests/unit/domain/test_models_spot.py tests/unit/domain/test_models_orderbook.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/funding_fee_bot/domain/models src/funding_fee_bot/domain/__init__.py tests/unit/domain/test_models_funding.py tests/unit/domain/test_models_spot.py tests/unit/domain/test_models_orderbook.py
git commit -m "refactor: split domain models by data capability"
```

### Task 3: Split CCXT Base into Core + Funding + Spot (+OrderBook placeholder)

**Files:**
- Create: `src/funding_fee_bot/providers/ccxt/core.py`
- Create: `src/funding_fee_bot/providers/ccxt/funding_base.py`
- Create: `src/funding_fee_bot/providers/ccxt/spot_base.py`
- Create: `src/funding_fee_bot/providers/ccxt/orderbook_base.py`
- Modify: `src/funding_fee_bot/providers/__init__.py`
- Test: `tests/unit/providers/funding/test_ccxt_funding_base.py`
- Test: `tests/unit/providers/spot/test_ccxt_spot_base.py`

**Step 1: Write the failing test**

```python
# tests/unit/providers/spot/test_ccxt_spot_base.py
from decimal import Decimal
from funding_fee_bot.providers.ccxt.spot_base import CcxtSpotProviderBase


class FakeSpotProvider(CcxtSpotProviderBase):
    exchange_id = "binance"


class FakeExchange:
    def load_markets(self):
        return None
    def fetch_ticker(self, symbol):
        return {"symbol": symbol, "last": 100.0, "bid": 99.0, "ask": 101.0, "timestamp": 1700000000000}


def test_fetch_spot_ticker_maps_model(monkeypatch):
    p = FakeSpotProvider()
    monkeypatch.setattr(p, "_make_exchange", lambda: FakeExchange())
    t = p.fetch_spot_ticker("BTC/USDT")
    assert t.last == Decimal("100.0")
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/providers/spot/test_ccxt_spot_base.py -v`
Expected: FAIL missing module/class

**Step 3: Write minimal implementation**

- `core.py`: shared exchange initialization, error mapping, helper conversion methods.
- `funding_base.py`: funding-only fetch/map methods from old base.
- `spot_base.py`: spot ticker fetch/map methods.
- `orderbook_base.py`: placeholder method contract.
- Keep temporary compatibility alias only if needed during refactor.

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/providers/funding/test_ccxt_funding_base.py tests/unit/providers/spot/test_ccxt_spot_base.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/funding_fee_bot/providers/ccxt src/funding_fee_bot/providers/__init__.py tests/unit/providers/funding/test_ccxt_funding_base.py tests/unit/providers/spot/test_ccxt_spot_base.py
git commit -m "refactor: split ccxt provider base by data type"
```

### Task 4: Refactor Exchange Providers to Compose Capabilities

**Files:**
- Modify: `src/funding_fee_bot/providers/binance.py`
- Modify: `src/funding_fee_bot/providers/bybit.py`
- Modify: `src/funding_fee_bot/providers/bitget.py`
- Modify: `src/funding_fee_bot/providers/__init__.py`
- Test: `tests/unit/providers/test_binance_provider.py`
- Test: `tests/unit/providers/test_bybit_provider.py`
- Test: `tests/unit/providers/test_bitget_provider.py`

**Step 1: Write the failing test**

```python
# tests/unit/providers/test_binance_provider.py
from funding_fee_bot.domain.capabilities import ProviderCapability
from funding_fee_bot.providers.binance import BinanceMarketDataProvider


def test_binance_declares_funding_and_spot_capabilities():
    p = BinanceMarketDataProvider()
    assert ProviderCapability.FUNDING_RATE in p.capabilities
    assert ProviderCapability.SPOT_PRICE in p.capabilities
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/providers/test_binance_provider.py tests/unit/providers/test_bybit_provider.py tests/unit/providers/test_bitget_provider.py -v`
Expected: FAIL outdated class names/capability attribute

**Step 3: Write minimal implementation**

- Exchange providers inherit needed bases only.
- Add `capabilities` set.
- Keep options for funding contracts as already defined.

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/providers/test_binance_provider.py tests/unit/providers/test_bybit_provider.py tests/unit/providers/test_bitget_provider.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/funding_fee_bot/providers/binance.py src/funding_fee_bot/providers/bybit.py src/funding_fee_bot/providers/bitget.py src/funding_fee_bot/providers/__init__.py tests/unit/providers/test_binance_provider.py tests/unit/providers/test_bybit_provider.py tests/unit/providers/test_bitget_provider.py
git commit -m "refactor: compose exchange providers by capabilities"
```

### Task 5: Replace FundingService with MarketDataService + Capability Guard

**Files:**
- Create: `src/funding_fee_bot/service/market_data_service.py`
- Modify: `src/funding_fee_bot/service/__init__.py`
- Modify: `src/funding_fee_bot/domain/errors.py`
- Test: `tests/unit/service/test_market_data_service.py`

**Step 1: Write the failing test**

```python
# tests/unit/service/test_market_data_service.py
import pytest
from funding_fee_bot.domain.capabilities import ProviderCapability
from funding_fee_bot.service.market_data_service import MarketDataService


def test_service_routes_provider():
    svc = MarketDataService()
    p = svc.get_provider("binance")
    assert p.supports(ProviderCapability.SPOT_PRICE)


def test_service_raises_for_unsupported_exchange():
    svc = MarketDataService()
    with pytest.raises(ValueError):
        svc.get_provider("unknown")
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/service/test_market_data_service.py -v`
Expected: FAIL missing service module/class

**Step 3: Write minimal implementation**

- Add `MarketDataService` routing.
- Add `UnsupportedCapabilityError` in domain errors.
- Export new service from package.

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/service/test_market_data_service.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/funding_fee_bot/service/market_data_service.py src/funding_fee_bot/service/__init__.py src/funding_fee_bot/domain/errors.py tests/unit/service/test_market_data_service.py
git commit -m "feat: add market data service with capability checks"
```

### Task 6: Update Documentation and Verify Full Suite

**Files:**
- Modify: `docs/architecture/funding-fee-fetcher.md`
- Create: `docs/architecture/market-data-provider.md`
- Modify: `README.md`

**Step 1: Write the failing test**

- Documentation task; no automated failing test required.
- Use a checklist assertion in PR notes:
  - architecture docs updated
  - README reflects `MarketDataService` and capabilities

**Step 2: Run checks to verify current state**

Run: `uv run pytest tests/unit -v`
Expected: PASS

**Step 3: Write minimal implementation**

- Add new architecture doc for capability-based design.
- Keep old funding-only doc as historical context or adjust title.
- Update README commands and terms.

**Step 4: Run verification to ensure all pass**

Run: `uv run pytest tests/unit -v`
Expected: PASS

Run: `RUN_LIVE_TESTS=1 uv run pytest tests/integration/test_binance_live.py -v`
Expected: PASS or SKIP based on env/network

**Step 5: Commit**

```bash
git add docs/architecture/funding-fee-fetcher.md docs/architecture/market-data-provider.md README.md
git commit -m "docs: describe capability-based market data architecture"
```

### Final Verification Checklist

- Run: `uv lock` (only if dependencies changed)
- Run: `uv sync --extra dev` (only if dependencies changed)
- Run: `uv run pytest tests/unit -v`
- Run: `git status --short`
- Confirm provider split by data type base classes
- Confirm no migration compatibility layer introduced
