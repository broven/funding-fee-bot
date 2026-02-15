from funding_fee_bot.providers.binance import BinanceFundingProvider


class FundingService:
    def get_provider(self, exchange: str):
        if exchange == "binance":
            return BinanceFundingProvider()
        raise ValueError(f"unsupported exchange: {exchange}")
