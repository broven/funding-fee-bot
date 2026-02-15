from decimal import Decimal

from funding_fee_bot.domain.models.spot import SpotTicker


def test_spot_ticker_model_shape():
    ticker = SpotTicker(
        exchange="binance",
        symbol="BTC/USDT",
        last=Decimal("60000"),
        bid=Decimal("59999"),
        ask=Decimal("60001"),
        timestamp=1700000000000,
        fetched_at=1700000000123,
    )

    assert ticker.symbol == "BTC/USDT"
