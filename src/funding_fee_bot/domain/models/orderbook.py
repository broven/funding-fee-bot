from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class OrderBookLevel:
    price: Decimal
    amount: Decimal


@dataclass(frozen=True)
class OrderBookSnapshot:
    exchange: str
    symbol: str
    bids: list[OrderBookLevel]
    asks: list[OrderBookLevel]
    timestamp: int | None
    fetched_at: int
