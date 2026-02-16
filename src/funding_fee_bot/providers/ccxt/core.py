import os

import ccxt

from funding_fee_bot.domain.interfaces import CapabilityAwareProvider


class CcxtProviderCore(CapabilityAwareProvider):
    exchange_id: str = ""

    def __init__(self, options: dict | None = None):
        self._options = self._build_options(options)
        self._exchange = None

    @classmethod
    def _build_options(cls, options: dict | None = None) -> dict:
        merged = dict(options or {})
        env_options = cls._read_env_options()
        for key, value in env_options.items():
            merged.setdefault(key, value)
        return merged

    @staticmethod
    def _read_env_options() -> dict:
        options: dict = {}

        timeout_raw = os.getenv("CCXT_TIMEOUT_MS") or os.getenv("CCXT_TIMEOUT")
        if timeout_raw:
            try:
                options["timeout"] = int(timeout_raw)
            except ValueError:
                pass

        https_proxy = (
            os.getenv("CCXT_HTTPS_PROXY")
            or os.getenv("HTTPS_PROXY")
            or os.getenv("https_proxy")
        )
        if https_proxy:
            options["httpsProxy"] = https_proxy
            return options

        socks_proxy = (
            os.getenv("CCXT_SOCKS_PROXY")
            or os.getenv("SOCKS_PROXY")
            or os.getenv("ALL_PROXY")
            or os.getenv("all_proxy")
        )
        if socks_proxy:
            options["socksProxy"] = socks_proxy
            return options

        http_proxy = (
            os.getenv("CCXT_HTTP_PROXY")
            or os.getenv("HTTP_PROXY")
            or os.getenv("http_proxy")
        )
        if http_proxy:
            options["httpProxy"] = http_proxy

        return options

    def _make_exchange(self):
        exchange_cls = getattr(ccxt, self.exchange_id)
        return exchange_cls(self._options)

    def _get_exchange(self):
        if self._exchange is None:
            self._exchange = self._make_exchange()
            self._exchange.load_markets()
        return self._exchange
