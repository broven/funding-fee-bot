from decimal import Decimal

from funding_fee_bot.providers.ccxt_base_provider import CcxtBaseProvider


class FakeProvider(CcxtBaseProvider):
    exchange_id = "binance"


class FakeExchange:
    def __init__(self):
        self.args = None

    def load_markets(self):
        return None

    def fetch_funding_rate_history(self, symbol, since=None, limit=None):
        self.args = (symbol, since, limit)
        return [
            {
                "symbol": "BTC/USDT:USDT",
                "fundingRate": 0.0001,
                "timestamp": 1700000000000,
            }
        ]


def test_fetch_history_maps_items(monkeypatch):
    provider = FakeProvider()
    exchange = FakeExchange()
    monkeypatch.setattr(provider, "_make_exchange", lambda: exchange)

    items = provider.fetch_history("BTC/USDT:USDT", since=1700000000000, limit=10)

    assert exchange.args == ("BTC/USDT:USDT", 1700000000000, 10)
    assert len(items) == 1
    assert items[0].funding_rate == Decimal("0.0001")
