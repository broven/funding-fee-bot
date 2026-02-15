from funding_fee_bot.domain.capabilities import ProviderCapability
from funding_fee_bot.domain.interfaces import (
    CapabilityAwareProvider,
    FundingRateProvider,
    OrderBookProvider,
    SpotPriceProvider,
)


def test_interface_exposes_ccxt_style_methods():
    required = {"fetch_current", "fetch_current_all", "fetch_history"}
    assert required.issubset(set(dir(FundingRateProvider)))


def test_new_interfaces_exist():
    assert hasattr(SpotPriceProvider, "fetch_spot_ticker")
    assert hasattr(OrderBookProvider, "fetch_order_book")


def test_capability_aware_provider_supports_method():
    class StubProvider(CapabilityAwareProvider):
        capabilities = {ProviderCapability.FUNDING_RATE}

    provider = StubProvider()

    assert provider.supports(ProviderCapability.FUNDING_RATE) is True
    assert provider.supports(ProviderCapability.SPOT_PRICE) is False
