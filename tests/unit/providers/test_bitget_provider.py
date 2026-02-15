from funding_fee_bot.domain.capabilities import ProviderCapability
from funding_fee_bot.providers.bitget import BitgetMarketDataProvider


def test_bitget_provider_declares_capabilities():
    provider = BitgetMarketDataProvider()
    assert provider.exchange_id == "bitget"
    assert provider.supports(ProviderCapability.FUNDING_RATE) is True
    assert provider.supports(ProviderCapability.SPOT_PRICE) is True
