from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class SpotTicker:
    exchange: str
    symbol: str
    last: Decimal | None
    bid: Decimal | None
    ask: Decimal | None
    timestamp: int | None
    fetched_at: int
