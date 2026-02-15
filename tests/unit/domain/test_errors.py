from funding_fee_bot.domain.errors import FundingRateLimitError


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
