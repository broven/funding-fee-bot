from funding_fee_bot.providers.binance import BinanceFundingProvider


def test_binance_provider_sets_exchange_id():
    provider = BinanceFundingProvider()
    assert provider.exchange_id == "binance"
