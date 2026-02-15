from funding_fee_bot.providers.ccxt_base_provider import CcxtBaseProvider


class BybitFundingProvider(CcxtBaseProvider):
    exchange_id = "bybit"

    def __init__(self):
        super().__init__(
            options={"options": {"defaultType": "swap", "defaultSubType": "linear"}}
        )
