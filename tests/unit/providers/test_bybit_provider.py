from funding_fee_bot.providers.bybit import BybitFundingProvider


def test_bybit_provider_sets_exchange_id_and_default_options():
    provider = BybitFundingProvider()
    assert provider.exchange_id == "bybit"
    assert provider._options["options"]["defaultType"] == "swap"
    assert provider._options["options"]["defaultSubType"] == "linear"
