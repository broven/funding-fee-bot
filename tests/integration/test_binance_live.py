import os

import pytest

from funding_fee_bot.providers.binance import BinanceMarketDataProvider


@pytest.mark.skipif(os.getenv("RUN_LIVE_TESTS") != "1", reason="set RUN_LIVE_TESTS=1")
def test_binance_live_fetch_current():
    provider = BinanceMarketDataProvider()
    result = provider.fetch_current("BTC/USDT:USDT")
    assert result.exchange == "binance"
