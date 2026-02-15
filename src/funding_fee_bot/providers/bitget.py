from funding_fee_bot.domain.capabilities import ProviderCapability
from funding_fee_bot.providers.ccxt.funding_base import CcxtFundingProviderBase
from funding_fee_bot.providers.ccxt.spot_base import CcxtSpotProviderBase


class BitgetMarketDataProvider(CcxtFundingProviderBase, CcxtSpotProviderBase):
    exchange_id = "bitget"
    capabilities = {
        ProviderCapability.FUNDING_RATE,
        ProviderCapability.SPOT_PRICE,
    }

    def __init__(self):
        super().__init__(
            options={"options": {"defaultType": "swap", "defaultSubType": "linear"}}
        )
