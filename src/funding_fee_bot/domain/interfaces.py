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
    def fetch_history(
        self,
        symbol: str,
        since: int | None = None,
        limit: int | None = None,
    ) -> list[FundingRateHistoryItem]:
        raise NotImplementedError
