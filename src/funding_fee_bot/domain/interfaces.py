from abc import ABC, abstractmethod

from .capabilities import ProviderCapability
from .models import (
    FundingRateCurrent,
    FundingRateHistoryItem,
    OrderBookSnapshot,
    SpotTicker,
)


class CapabilityAwareProvider(ABC):
    capabilities: set[ProviderCapability] = set()

    def supports(self, capability: ProviderCapability) -> bool:
        return capability in self.capabilities


class FundingRateProvider(ABC):
    @abstractmethod
    def fetch_current(self, symbol: str) -> FundingRateCurrent:
        raise NotImplementedError

    @abstractmethod
    def fetch_current_all(self) -> list[FundingRateCurrent]:
        raise NotImplementedError

    @abstractmethod
    def fetch_history(
        self,
        symbol: str,
        since: int | None = None,
        limit: int | None = None,
    ) -> list[FundingRateHistoryItem]:
        raise NotImplementedError


class SpotPriceProvider(ABC):
    @abstractmethod
    def fetch_spot_ticker(self, symbol: str) -> SpotTicker:
        raise NotImplementedError


class OrderBookProvider(ABC):
    @abstractmethod
    def fetch_order_book(
        self,
        symbol: str,
        limit: int | None = None,
    ) -> OrderBookSnapshot:
        raise NotImplementedError
