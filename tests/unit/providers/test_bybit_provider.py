from funding_fee_bot.domain.capabilities import ProviderCapability
from funding_fee_bot.providers.bybit import BybitMarketDataProvider


def test_bybit_provider_declares_capabilities():
    provider = BybitMarketDataProvider()
    assert provider.exchange_id == "bybit"
    assert provider.supports(ProviderCapability.FUNDING_RATE) is True
    assert provider.supports(ProviderCapability.SPOT_PRICE) is True
