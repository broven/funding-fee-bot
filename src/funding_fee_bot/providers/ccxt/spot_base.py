import time
from decimal import Decimal

from funding_fee_bot.domain.interfaces import SpotPriceProvider
from funding_fee_bot.domain.models import SpotTicker

from .core import CcxtProviderCore


class CcxtSpotProviderBase(CcxtProviderCore, SpotPriceProvider):
    def fetch_spot_ticker(self, symbol: str) -> SpotTicker:
        exchange = self._get_exchange()
        raw = exchange.fetch_ticker(symbol)
        return SpotTicker(
            exchange=self.exchange_id,
            symbol=raw.get("symbol") or symbol,
            last=Decimal(str(raw["last"])) if raw.get("last") is not None else None,
            bid=Decimal(str(raw["bid"])) if raw.get("bid") is not None else None,
            ask=Decimal(str(raw["ask"])) if raw.get("ask") is not None else None,
            timestamp=raw.get("timestamp"),
            fetched_at=int(time.time() * 1000),
        )
