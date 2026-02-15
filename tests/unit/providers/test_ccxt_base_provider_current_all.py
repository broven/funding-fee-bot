from funding_fee_bot.providers.ccxt_base_provider import CcxtBaseProvider


class FakeProvider(CcxtBaseProvider):
    exchange_id = "binance"


class FakeExchange:
    def load_markets(self):
        return None

    def fetch_funding_rates(self):
        return {
            "BTC/USDT:USDT": {
                "symbol": "BTC/USDT:USDT",
                "fundingRate": 0.0001,
                "timestamp": 1,
                "nextFundingTimestamp": 2,
            }
        }


def test_fetch_current_all_returns_list(monkeypatch):
    provider = FakeProvider()
    monkeypatch.setattr(provider, "_make_exchange", lambda: FakeExchange())

    result = provider.fetch_current_all()

    assert len(result) == 1
    assert result[0].symbol == "BTC/USDT:USDT"
