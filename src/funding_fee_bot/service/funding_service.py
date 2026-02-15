from funding_fee_bot.providers.binance import BinanceFundingProvider
from funding_fee_bot.providers.bitget import BitgetFundingProvider
from funding_fee_bot.providers.bybit import BybitFundingProvider


class FundingService:
    def get_provider(self, exchange: str):
        providers = {
            "binance": BinanceFundingProvider,
            "bybit": BybitFundingProvider,
            "bitget": BitgetFundingProvider,
        }
        provider_cls = providers.get(exchange)
        if provider_cls:
            return provider_cls()
        raise ValueError(f"unsupported exchange: {exchange}")
