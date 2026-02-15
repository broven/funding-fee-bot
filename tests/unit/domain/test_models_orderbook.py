from decimal import Decimal

from funding_fee_bot.domain.models.orderbook import OrderBookLevel, OrderBookSnapshot


def test_orderbook_snapshot_model_shape():
    snapshot = OrderBookSnapshot(
        exchange="binance",
        symbol="BTC/USDT",
        bids=[OrderBookLevel(price=Decimal("59999"), amount=Decimal("1.2"))],
        asks=[OrderBookLevel(price=Decimal("60001"), amount=Decimal("0.8"))],
        timestamp=1700000000000,
        fetched_at=1700000000123,
    )

    assert snapshot.bids[0].price == Decimal("59999")
