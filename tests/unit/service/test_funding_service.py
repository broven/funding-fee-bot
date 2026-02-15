import pytest

from funding_fee_bot.service.funding_service import FundingService


@pytest.mark.parametrize(
    ("exchange", "expected_exchange_id"),
    [
        ("binance", "binance"),
        ("bybit", "bybit"),
        ("bitget", "bitget"),
    ],
)
def test_service_routes_exchange_provider(exchange, expected_exchange_id):
    service = FundingService()
    provider = service.get_provider(exchange)
    assert provider.exchange_id == expected_exchange_id
