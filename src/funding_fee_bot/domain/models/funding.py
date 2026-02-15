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
