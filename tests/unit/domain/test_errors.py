from funding_fee_bot.domain.errors import (
    FundingRateLimitError,
    UnsupportedCapabilityError,
)


def test_error_has_retryable_and_context():
    err = FundingRateLimitError(
        exchange="binance",
        operation="fetch_current",
        symbol="BTC/USDT:USDT",
        retryable=True,
        message="limited",
    )

    assert err.retryable is True
    assert err.exchange == "binance"


def test_unsupported_capability_error_has_context():
    err = UnsupportedCapabilityError("binance", "order_book")

    assert err.exchange == "binance"
    assert err.capability == "order_book"
