# Funding Fee Fetcher Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python funding-fee data fetcher with a ccxt-style unified provider interface, a reusable `CcxtBaseProvider`, and a Binance implementation that supports current(single/all) and history queries.

**Architecture:** The domain layer defines stable interfaces/models/errors. `CcxtBaseProvider` implements shared ccxt fetching/mapping/error conversion. Exchange-specific providers (e.g., Binance) only set exchange identity/options. A thin service routes provider selection without exposing ccxt to callers.

**Tech Stack:** Python 3.11+, `ccxt`, `pytest`, `pytest-mock`, `dataclasses`, `decimal`

---

### Task 1: Bootstrap Python Project and Test Harness

**Files:**
- Create: `pyproject.toml`
- Create: `src/funding_fee_bot/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/unit/test_package_smoke.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_package_smoke.py
import funding_fee_bot


def test_package_has_version():
    assert hasattr(funding_fee_bot, "__version__")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_package_smoke.py -v`
Expected: FAIL with missing module or missing `__version__`

**Step 3: Write minimal implementation**

```python
# src/funding_fee_bot/__init__.py
__version__ = "0.1.0"
```

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "funding-fee-bot"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["ccxt>=4.4.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-mock>=3.14"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_package_smoke.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add pyproject.toml src/funding_fee_bot/__init__.py tests/conftest.py tests/unit/test_package_smoke.py
git commit -m "chore: bootstrap python package and test harness"
```

### Task 2: Add Domain Models and Unified Errors

**Files:**
- Create: `src/funding_fee_bot/domain/models.py`
- Create: `src/funding_fee_bot/domain/errors.py`
- Create: `src/funding_fee_bot/domain/__init__.py`
- Test: `tests/unit/domain/test_models.py`
- Test: `tests/unit/domain/test_errors.py`

**Step 1: Write the failing test**

```python
# tests/unit/domain/test_models.py
from decimal import Decimal
from funding_fee_bot.domain.models import FundingRateCurrent


def test_current_model_uses_decimal_and_ms_fields():
    m = FundingRateCurrent(
        exchange="binance",
        symbol="BTC/USDT:USDT",
        funding_rate=Decimal("0.0001"),
        funding_timestamp=1700000000000,
        next_funding_timestamp=1700028800000,
        fetched_at=1700000000123,
    )
    assert m.funding_rate == Decimal("0.0001")
```

```python
# tests/unit/domain/test_errors.py
from funding_fee_bot.domain.errors import FundingRateLimitError


def test_error_has_retryable_and_context():
    err = FundingRateLimitError(
        exchange="binance",
        operation="fetch_current",
        symbol="BTC/USDT:USDT",
        retryable=True,
        message="limited",
    )
    assert err.retryable is True
    assert err.exchange == "binance"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/domain/test_models.py tests/unit/domain/test_errors.py -v`
Expected: FAIL with import error

**Step 3: Write minimal implementation**

```python
# src/funding_fee_bot/domain/models.py
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class FundingRateCurrent:
    exchange: str
    symbol: str
    funding_rate: Decimal
    funding_timestamp: int | None
    next_funding_timestamp: int | None
    fetched_at: int


@dataclass(frozen=True)
class FundingRateHistoryItem:
    exchange: str
    symbol: str
    funding_rate: Decimal
    funding_timestamp: int
    fetched_at: int
```

```python
# src/funding_fee_bot/domain/errors.py
class FundingProviderError(Exception):
    def __init__(self, exchange: str, operation: str, message: str, symbol: str | None = None, retryable: bool = False):
        super().__init__(message)
        self.exchange = exchange
        self.operation = operation
        self.symbol = symbol
        self.retryable = retryable


class FundingNetworkError(FundingProviderError):
    pass


class FundingRateLimitError(FundingProviderError):
    pass


class FundingSymbolNotFoundError(FundingProviderError):
    pass


class FundingDataError(FundingProviderError):
    pass
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/domain/test_models.py tests/unit/domain/test_errors.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/funding_fee_bot/domain/__init__.py src/funding_fee_bot/domain/models.py src/funding_fee_bot/domain/errors.py tests/unit/domain/test_models.py tests/unit/domain/test_errors.py
git commit -m "feat: add domain models and funding provider errors"
```

### Task 3: Define Unified Provider Interface

**Files:**
- Create: `src/funding_fee_bot/domain/interfaces.py`
- Modify: `src/funding_fee_bot/domain/__init__.py`
- Test: `tests/unit/domain/test_interfaces.py`

**Step 1: Write the failing test**

```python
# tests/unit/domain/test_interfaces.py
from funding_fee_bot.domain.interfaces import FundingRateProvider


def test_interface_exposes_ccxt_style_methods():
    required = {"fetch_current", "fetch_current_all", "fetch_history"}
    assert required.issubset(set(dir(FundingRateProvider)))
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/domain/test_interfaces.py -v`
Expected: FAIL import error

**Step 3: Write minimal implementation**

```python
# src/funding_fee_bot/domain/interfaces.py
from abc import ABC, abstractmethod
from .models import FundingRateCurrent, FundingRateHistoryItem


class FundingRateProvider(ABC):
    @abstractmethod
    def fetch_current(self, symbol: str) -> FundingRateCurrent:
        raise NotImplementedError

    @abstractmethod
    def fetch_current_all(self) -> list[FundingRateCurrent]:
        raise NotImplementedError

    @abstractmethod
    def fetch_history(self, symbol: str, since: int | None = None, limit: int | None = None) -> list[FundingRateHistoryItem]:
        raise NotImplementedError
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/domain/test_interfaces.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/funding_fee_bot/domain/interfaces.py src/funding_fee_bot/domain/__init__.py tests/unit/domain/test_interfaces.py
git commit -m "feat: define unified funding rate provider interface"
```

### Task 4: Implement `CcxtBaseProvider` Single-Symbol Current Fetch

**Files:**
- Create: `src/funding_fee_bot/providers/ccxt_base_provider.py`
- Create: `src/funding_fee_bot/providers/__init__.py`
- Test: `tests/unit/providers/test_ccxt_base_provider_current.py`

**Step 1: Write the failing test**

```python
# tests/unit/providers/test_ccxt_base_provider_current.py
from decimal import Decimal
from funding_fee_bot.providers.ccxt_base_provider import CcxtBaseProvider


class FakeProvider(CcxtBaseProvider):
    exchange_id = "binance"


def test_fetch_current_maps_to_standard_model(mocker):
    p = FakeProvider()
    mock_exchange = mocker.Mock()
    mock_exchange.fetch_funding_rate.return_value = {
        "symbol": "BTC/USDT:USDT",
        "fundingRate": 0.0001,
        "timestamp": 1700000000000,
        "nextFundingTimestamp": 1700028800000,
    }
    mocker.patch.object(p, "_make_exchange", return_value=mock_exchange)

    result = p.fetch_current("BTC/USDT:USDT")
    assert result.exchange == "binance"
    assert result.funding_rate == Decimal("0.0001")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/providers/test_ccxt_base_provider_current.py -v`
Expected: FAIL with missing class/method

**Step 3: Write minimal implementation**

```python
# src/funding_fee_bot/providers/ccxt_base_provider.py
import time
from decimal import Decimal
import ccxt
from funding_fee_bot.domain.interfaces import FundingRateProvider
from funding_fee_bot.domain.models import FundingRateCurrent, FundingRateHistoryItem
from funding_fee_bot.domain.errors import FundingDataError, FundingNetworkError, FundingRateLimitError, FundingSymbolNotFoundError


class CcxtBaseProvider(FundingRateProvider):
    exchange_id: str = ""

    def __init__(self, options: dict | None = None):
        self._options = options or {}
        self._exchange = None

    def _make_exchange(self):
        exchange_cls = getattr(ccxt, self.exchange_id)
        return exchange_cls(self._options)

    def _get_exchange(self):
        if self._exchange is None:
            self._exchange = self._make_exchange()
            self._exchange.load_markets()
        return self._exchange

    def fetch_current(self, symbol: str) -> FundingRateCurrent:
        ex = self._get_exchange()
        try:
            raw = ex.fetch_funding_rate(symbol)
            return FundingRateCurrent(
                exchange=self.exchange_id,
                symbol=raw.get("symbol") or symbol,
                funding_rate=Decimal(str(raw["fundingRate"])),
                funding_timestamp=raw.get("timestamp"),
                next_funding_timestamp=raw.get("nextFundingTimestamp"),
                fetched_at=int(time.time() * 1000),
            )
        except ccxt.BadSymbol as e:
            raise FundingSymbolNotFoundError(self.exchange_id, "fetch_current", str(e), symbol=symbol, retryable=False) from e
        except ccxt.RateLimitExceeded as e:
            raise FundingRateLimitError(self.exchange_id, "fetch_current", str(e), symbol=symbol, retryable=True) from e
        except ccxt.NetworkError as e:
            raise FundingNetworkError(self.exchange_id, "fetch_current", str(e), symbol=symbol, retryable=True) from e
        except KeyError as e:
            raise FundingDataError(self.exchange_id, "fetch_current", f"missing field: {e}", symbol=symbol, retryable=False) from e
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/providers/test_ccxt_base_provider_current.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/funding_fee_bot/providers/ccxt_base_provider.py src/funding_fee_bot/providers/__init__.py tests/unit/providers/test_ccxt_base_provider_current.py
git commit -m "feat: add ccxt base provider current funding fetch"
```

### Task 5: Implement All-Symbol Current and History Fetch in Base Provider

**Files:**
- Modify: `src/funding_fee_bot/providers/ccxt_base_provider.py`
- Test: `tests/unit/providers/test_ccxt_base_provider_current_all.py`
- Test: `tests/unit/providers/test_ccxt_base_provider_history.py`

**Step 1: Write the failing test**

```python
# tests/unit/providers/test_ccxt_base_provider_current_all.py
from funding_fee_bot.providers.ccxt_base_provider import CcxtBaseProvider


class FakeProvider(CcxtBaseProvider):
    exchange_id = "binance"


def test_fetch_current_all_returns_list(mocker):
    p = FakeProvider()
    mock_exchange = mocker.Mock()
    mock_exchange.fetch_funding_rates.return_value = {
        "BTC/USDT:USDT": {"symbol": "BTC/USDT:USDT", "fundingRate": 0.0001, "timestamp": 1, "nextFundingTimestamp": 2}
    }
    mocker.patch.object(p, "_make_exchange", return_value=mock_exchange)
    assert len(p.fetch_current_all()) == 1
```

```python
# tests/unit/providers/test_ccxt_base_provider_history.py
class FakeProvider(CcxtBaseProvider):
    exchange_id = "binance"


def test_fetch_history_maps_items(mocker):
    p = FakeProvider()
    mock_exchange = mocker.Mock()
    mock_exchange.fetch_funding_rate_history.return_value = [
        {"symbol": "BTC/USDT:USDT", "fundingRate": 0.0001, "timestamp": 1700000000000}
    ]
    mocker.patch.object(p, "_make_exchange", return_value=mock_exchange)
    items = p.fetch_history("BTC/USDT:USDT", since=1700000000000, limit=10)
    assert len(items) == 1
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/providers/test_ccxt_base_provider_current_all.py tests/unit/providers/test_ccxt_base_provider_history.py -v`
Expected: FAIL with `NotImplementedError` or missing methods

**Step 3: Write minimal implementation**

```python
# in CcxtBaseProvider

def fetch_current_all(self) -> list[FundingRateCurrent]:
    ex = self._get_exchange()
    raw_map = ex.fetch_funding_rates()
    results: list[FundingRateCurrent] = []
    for _, raw in raw_map.items():
        results.append(
            FundingRateCurrent(
                exchange=self.exchange_id,
                symbol=raw["symbol"],
                funding_rate=Decimal(str(raw["fundingRate"])),
                funding_timestamp=raw.get("timestamp"),
                next_funding_timestamp=raw.get("nextFundingTimestamp"),
                fetched_at=int(time.time() * 1000),
            )
        )
    return results


def fetch_history(self, symbol: str, since: int | None = None, limit: int | None = None) -> list[FundingRateHistoryItem]:
    ex = self._get_exchange()
    rows = ex.fetch_funding_rate_history(symbol, since=since, limit=limit)
    return [
        FundingRateHistoryItem(
            exchange=self.exchange_id,
            symbol=row.get("symbol") or symbol,
            funding_rate=Decimal(str(row["fundingRate"])),
            funding_timestamp=row["timestamp"],
            fetched_at=int(time.time() * 1000),
        )
        for row in rows
    ]
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/providers/test_ccxt_base_provider_current_all.py tests/unit/providers/test_ccxt_base_provider_history.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/funding_fee_bot/providers/ccxt_base_provider.py tests/unit/providers/test_ccxt_base_provider_current_all.py tests/unit/providers/test_ccxt_base_provider_history.py
git commit -m "feat: add ccxt base provider all/current history fetch"
```

### Task 6: Add Binance Provider and Routing Service

**Files:**
- Create: `src/funding_fee_bot/providers/binance.py`
- Create: `src/funding_fee_bot/service/funding_service.py`
- Create: `src/funding_fee_bot/service/__init__.py`
- Test: `tests/unit/providers/test_binance_provider.py`
- Test: `tests/unit/service/test_funding_service.py`

**Step 1: Write the failing test**

```python
# tests/unit/providers/test_binance_provider.py
from funding_fee_bot.providers.binance import BinanceFundingProvider


def test_binance_provider_sets_exchange_id():
    p = BinanceFundingProvider()
    assert p.exchange_id == "binance"
```

```python
# tests/unit/service/test_funding_service.py
from funding_fee_bot.service.funding_service import FundingService


def test_service_routes_exchange_provider():
    svc = FundingService()
    provider = svc.get_provider("binance")
    assert provider.exchange_id == "binance"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/providers/test_binance_provider.py tests/unit/service/test_funding_service.py -v`
Expected: FAIL import error

**Step 3: Write minimal implementation**

```python
# src/funding_fee_bot/providers/binance.py
from funding_fee_bot.providers.ccxt_base_provider import CcxtBaseProvider


class BinanceFundingProvider(CcxtBaseProvider):
    exchange_id = "binance"

    def __init__(self):
        super().__init__(options={"options": {"defaultType": "future"}})
```

```python
# src/funding_fee_bot/service/funding_service.py
from funding_fee_bot.providers.binance import BinanceFundingProvider


class FundingService:
    def get_provider(self, exchange: str):
        if exchange == "binance":
            return BinanceFundingProvider()
        raise ValueError(f"unsupported exchange: {exchange}")
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/providers/test_binance_provider.py tests/unit/service/test_funding_service.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/funding_fee_bot/providers/binance.py src/funding_fee_bot/service/funding_service.py src/funding_fee_bot/service/__init__.py tests/unit/providers/test_binance_provider.py tests/unit/service/test_funding_service.py
git commit -m "feat: add binance provider and funding service router"
```

### Task 7: Verify End-to-End Unit Suite and Add Optional Live Integration Test

**Files:**
- Create: `tests/integration/test_binance_live.py`
- Modify: `README.md`

**Step 1: Write the failing test**

```python
# tests/integration/test_binance_live.py
import os
import pytest
from funding_fee_bot.providers.binance import BinanceFundingProvider


@pytest.mark.skipif(os.getenv("RUN_LIVE_TESTS") != "1", reason="set RUN_LIVE_TESTS=1")
def test_binance_live_fetch_current():
    p = BinanceFundingProvider()
    result = p.fetch_current("BTC/USDT:USDT")
    assert result.exchange == "binance"
```

**Step 2: Run test to verify it fails**

Run: `RUN_LIVE_TESTS=1 pytest tests/integration/test_binance_live.py -v`
Expected: FAIL initially if networking/options not aligned

**Step 3: Write minimal implementation**

- Adjust only provider options/market loading if needed.
- Keep interface unchanged.

**Step 4: Run tests to verify they pass**

Run: `pytest tests/unit -v`
Expected: PASS

Run: `RUN_LIVE_TESTS=1 pytest tests/integration/test_binance_live.py -v`
Expected: PASS (network-dependent)

**Step 5: Commit**

```bash
git add tests/integration/test_binance_live.py README.md
git commit -m "test: add optional binance live integration check"
```

### Final Verification Checklist

- Run: `pytest tests/unit -v`
- Run: `python -m pip check`
- Run: `git status --short`
- Confirm no interface leaks of ccxt types to service/domain layers
- Confirm provider filenames use exchange names only (`binance.py`)
