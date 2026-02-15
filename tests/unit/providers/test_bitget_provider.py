from funding_fee_bot.providers.bitget import BitgetFundingProvider


def test_bitget_provider_sets_exchange_id_and_default_options():
    provider = BitgetFundingProvider()
    assert provider.exchange_id == "bitget"
    assert provider._options["options"]["defaultType"] == "swap"
    assert provider._options["options"]["defaultSubType"] == "linear"
