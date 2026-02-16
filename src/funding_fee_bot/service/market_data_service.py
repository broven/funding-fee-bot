from funding_fee_bot.domain.capabilities import ProviderCapability
from funding_fee_bot.domain.errors import UnsupportedCapabilityError
from funding_fee_bot.providers.binance import BinanceMarketDataProvider
from funding_fee_bot.providers.bitget import BitgetMarketDataProvider
from funding_fee_bot.providers.bybit import BybitMarketDataProvider


class MarketDataService:
    def __init__(self, providers: dict[str, type] | None = None):
        self._providers = providers or {
            "binance": BinanceMarketDataProvider,
            "bybit": BybitMarketDataProvider,
            "bitget": BitgetMarketDataProvider,
        }

    def available_exchanges(self) -> list[str]:
        return list(self._providers.keys())

    def get_provider(
        self,
        exchange: str,
        required_capability: ProviderCapability | None = None,
    ):
        provider_cls = self._providers.get(exchange)
        if provider_cls is None:
            raise ValueError(f"unsupported exchange: {exchange}")

        provider = provider_cls()
        if required_capability and not provider.supports(required_capability):
            raise UnsupportedCapabilityError(exchange, required_capability.value)

        return provider
