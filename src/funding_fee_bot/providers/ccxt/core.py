import os

import ccxt

from funding_fee_bot.domain.interfaces import CapabilityAwareProvider


class CcxtProviderCore(CapabilityAwareProvider):
    exchange_id: str = ""

    def __init__(self, options: dict | None = None):
        self._options = options or {}
        self._exchange = None

    def _make_exchange(self):
        exchange_cls = getattr(ccxt, self.exchange_id)
        opts = {**self._options}
        proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
        if proxy:
            opts["httpsProxy"] = proxy
        return exchange_cls(opts)

    def _get_exchange(self):
        if self._exchange is None:
            self._exchange = self._make_exchange()
            self._exchange.load_markets()
        return self._exchange
