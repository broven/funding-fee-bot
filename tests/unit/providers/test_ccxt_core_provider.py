from funding_fee_bot.providers.ccxt.core import CcxtProviderCore


class FakeCoreProvider(CcxtProviderCore):
    exchange_id = "binance"


def test_core_reads_https_proxy_and_timeout_from_env(monkeypatch):
    monkeypatch.setenv("CCXT_HTTPS_PROXY", "http://127.0.0.1:6152")
    monkeypatch.setenv("CCXT_TIMEOUT_MS", "60000")

    provider = FakeCoreProvider(options={"options": {"defaultType": "future"}})

    assert provider._options["httpsProxy"] == "http://127.0.0.1:6152"
    assert provider._options["timeout"] == 60000
    assert provider._options["options"]["defaultType"] == "future"


def test_core_prefers_explicit_options_over_env(monkeypatch):
    monkeypatch.setenv("CCXT_HTTPS_PROXY", "http://127.0.0.1:6152")
    monkeypatch.setenv("CCXT_TIMEOUT_MS", "60000")

    provider = FakeCoreProvider(
        options={
            "options": {"defaultType": "future"},
            "httpsProxy": "http://127.0.0.1:9999",
            "timeout": 12345,
        }
    )

    assert provider._options["httpsProxy"] == "http://127.0.0.1:9999"
    assert provider._options["timeout"] == 12345


def test_core_uses_https_proxy_fallback_env(monkeypatch):
    monkeypatch.delenv("CCXT_HTTPS_PROXY", raising=False)
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:6152")

    provider = FakeCoreProvider()

    assert provider._options["httpsProxy"] == "http://127.0.0.1:6152"
