from funding_fee_bot.domain.capabilities import ProviderCapability


def test_capabilities_enum_contains_expected_values():
    assert ProviderCapability.FUNDING_RATE.value == "funding_rate"
    assert ProviderCapability.SPOT_PRICE.value == "spot_price"
    assert ProviderCapability.ORDER_BOOK.value == "order_book"
