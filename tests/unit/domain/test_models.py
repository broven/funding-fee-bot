from decimal import Decimal

from funding_fee_bot.domain.models import FundingRateCurrent


def test_current_model_uses_decimal_and_ms_fields():
    model = FundingRateCurrent(
        exchange="binance",
        symbol="BTC/USDT:USDT",
        funding_rate=Decimal("0.0001"),
        funding_timestamp=1700000000000,
        next_funding_timestamp=1700028800000,
        fetched_at=1700000000123,
    )

    assert model.funding_rate == Decimal("0.0001")
