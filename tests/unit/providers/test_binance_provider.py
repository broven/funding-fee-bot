from funding_fee_bot.domain.capabilities import ProviderCapability
from funding_fee_bot.providers.binance import BinanceMarketDataProvider


def test_binance_provider_declares_capabilities():
    provider = BinanceMarketDataProvider()
    assert provider.exchange_id == "binance"
    assert ProviderCapability.FUNDING_RATE in provider.capabilities
    assert ProviderCapability.SPOT_PRICE in provider.capabilities
