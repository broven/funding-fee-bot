from funding_fee_bot.service.funding_service import FundingService


def test_service_routes_exchange_provider():
    service = FundingService()
    provider = service.get_provider("binance")
    assert provider.exchange_id == "binance"
