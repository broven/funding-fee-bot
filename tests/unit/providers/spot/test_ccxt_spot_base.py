from decimal import Decimal

from funding_fee_bot.providers.ccxt.spot_base import CcxtSpotProviderBase


class FakeSpotProvider(CcxtSpotProviderBase):
    exchange_id = "binance"


class FakeExchange:
    def load_markets(self):
        return None

    def fetch_ticker(self, symbol):
        return {
            "symbol": symbol,
            "last": 100.0,
            "bid": 99.0,
            "ask": 101.0,
            "timestamp": 1700000000000,
        }


def test_fetch_spot_ticker_maps_model(monkeypatch):
    provider = FakeSpotProvider()
    monkeypatch.setattr(provider, "_make_exchange", lambda: FakeExchange())

    ticker = provider.fetch_spot_ticker("BTC/USDT")

    assert ticker.exchange == "binance"
    assert ticker.symbol == "BTC/USDT"
    assert ticker.last == Decimal("100.0")
