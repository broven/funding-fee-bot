from decimal import Decimal

from funding_fee_bot.providers.ccxt.funding_base import CcxtFundingProviderBase


class FakeFundingProvider(CcxtFundingProviderBase):
    exchange_id = "binance"


class FakeExchange:
    def load_markets(self):
        return None

    def fetch_funding_rate(self, symbol):
        return {
            "symbol": symbol,
            "fundingRate": 0.0001,
            "timestamp": 1700000000000,
            "nextFundingTimestamp": 1700028800000,
        }


def test_fetch_current_maps_to_standard_model(monkeypatch):
    provider = FakeFundingProvider()
    monkeypatch.setattr(provider, "_make_exchange", lambda: FakeExchange())

    result = provider.fetch_current("BTC/USDT:USDT")

    assert result.exchange == "binance"
    assert result.symbol == "BTC/USDT:USDT"
    assert result.funding_rate == Decimal("0.0001")
