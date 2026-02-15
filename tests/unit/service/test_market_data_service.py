import pytest

from funding_fee_bot.domain.capabilities import ProviderCapability
from funding_fee_bot.domain.errors import UnsupportedCapabilityError
from funding_fee_bot.service.market_data_service import MarketDataService


def test_service_routes_provider():
    service = MarketDataService()
    provider = service.get_provider("binance")
    assert provider.supports(ProviderCapability.SPOT_PRICE) is True


def test_service_raises_for_unsupported_exchange():
    service = MarketDataService()
    with pytest.raises(ValueError):
        service.get_provider("unknown")


def test_service_raises_for_unsupported_capability():
    class SpotOnlyStub:
        exchange_id = "stub"
        capabilities = {ProviderCapability.SPOT_PRICE}

        def supports(self, capability: ProviderCapability) -> bool:
            return capability in self.capabilities

    service = MarketDataService(providers={"stub": SpotOnlyStub})
    with pytest.raises(UnsupportedCapabilityError):
        service.get_provider("stub", required_capability=ProviderCapability.FUNDING_RATE)
