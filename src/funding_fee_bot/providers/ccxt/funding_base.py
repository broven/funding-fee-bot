import time
from decimal import Decimal

import ccxt

from funding_fee_bot.domain.errors import (
    FundingDataError,
    FundingNetworkError,
    FundingRateLimitError,
    FundingSymbolNotFoundError,
)
from funding_fee_bot.domain.interfaces import FundingRateProvider
from funding_fee_bot.domain.models import FundingRateCurrent, FundingRateHistoryItem

from .core import CcxtProviderCore


class CcxtFundingProviderBase(CcxtProviderCore, FundingRateProvider):
    def fetch_current(self, symbol: str) -> FundingRateCurrent:
        exchange = self._get_exchange()
        try:
            raw = exchange.fetch_funding_rate(symbol)
            return FundingRateCurrent(
                exchange=self.exchange_id,
                symbol=raw.get("symbol") or symbol,
                funding_rate=Decimal(str(raw["fundingRate"])),
                funding_timestamp=raw.get("timestamp"),
                next_funding_timestamp=raw.get("nextFundingTimestamp"),
                fetched_at=int(time.time() * 1000),
            )
        except ccxt.BadSymbol as exc:
            raise FundingSymbolNotFoundError(
                exchange=self.exchange_id,
                operation="fetch_current",
                symbol=symbol,
                retryable=False,
                message=str(exc),
            ) from exc
        except ccxt.RateLimitExceeded as exc:
            raise FundingRateLimitError(
                exchange=self.exchange_id,
                operation="fetch_current",
                symbol=symbol,
                retryable=True,
                message=str(exc),
            ) from exc
        except ccxt.NetworkError as exc:
            raise FundingNetworkError(
                exchange=self.exchange_id,
                operation="fetch_current",
                symbol=symbol,
                retryable=True,
                message=str(exc),
            ) from exc
        except KeyError as exc:
            raise FundingDataError(
                exchange=self.exchange_id,
                operation="fetch_current",
                symbol=symbol,
                retryable=False,
                message=f"missing field: {exc}",
            ) from exc

    def fetch_current_all(self) -> list[FundingRateCurrent]:
        exchange = self._get_exchange()
        raw_map = exchange.fetch_funding_rates()
        fetched_at = int(time.time() * 1000)
        rows = raw_map.values() if isinstance(raw_map, dict) else raw_map

        return [
            FundingRateCurrent(
                exchange=self.exchange_id,
                symbol=raw["symbol"],
                funding_rate=Decimal(str(raw["fundingRate"])),
                funding_timestamp=raw.get("timestamp"),
                next_funding_timestamp=raw.get("nextFundingTimestamp"),
                fetched_at=fetched_at,
            )
            for raw in rows
        ]

    def fetch_history(
        self,
        symbol: str,
        since: int | None = None,
        limit: int | None = None,
    ) -> list[FundingRateHistoryItem]:
        exchange = self._get_exchange()
        rows = exchange.fetch_funding_rate_history(symbol, since=since, limit=limit)
        fetched_at = int(time.time() * 1000)

        return [
            FundingRateHistoryItem(
                exchange=self.exchange_id,
                symbol=row.get("symbol") or symbol,
                funding_rate=Decimal(str(row["fundingRate"])),
                funding_timestamp=row["timestamp"],
                fetched_at=fetched_at,
            )
            for row in rows
        ]
