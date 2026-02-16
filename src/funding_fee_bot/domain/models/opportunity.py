from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class SpotPerpDirection(str, Enum):
    LONG_SPOT_SHORT_PERP = "long_spot_short_perp"
    SHORT_SPOT_LONG_PERP = "short_spot_long_perp"


@dataclass(frozen=True)
class PerpPerpOpportunity:
    symbol: str
    long_exchange: str
    long_symbol: str
    long_funding_rate: Decimal
    short_exchange: str
    short_symbol: str
    short_funding_rate: Decimal
    funding_rate_spread: Decimal


@dataclass(frozen=True)
class SpotPerpOpportunity:
    symbol: str
    exchange: str
    perp_symbol: str
    funding_rate: Decimal
    direction: SpotPerpDirection
    expected_funding_edge: Decimal
    spot_last: Decimal | None
