import ccxt

from funding_fee_bot.domain.interfaces import CapabilityAwareProvider


class CcxtProviderCore(CapabilityAwareProvider):
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
