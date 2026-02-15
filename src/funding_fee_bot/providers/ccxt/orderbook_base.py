from funding_fee_bot.domain.interfaces import OrderBookProvider

from .core import CcxtProviderCore


class CcxtOrderBookProviderBase(CcxtProviderCore, OrderBookProvider):
    def fetch_order_book(self, symbol: str, limit: int | None = None):
        raise NotImplementedError
