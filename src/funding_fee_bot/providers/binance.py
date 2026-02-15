from funding_fee_bot.providers.ccxt_base_provider import CcxtBaseProvider


class BinanceFundingProvider(CcxtBaseProvider):
    exchange_id = "binance"

    def __init__(self):
        super().__init__(options={"options": {"defaultType": "future"}})
