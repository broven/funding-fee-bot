from funding_fee_bot.domain.interfaces import FundingRateProvider


def test_interface_exposes_ccxt_style_methods():
    required = {"fetch_current", "fetch_current_all", "fetch_history"}
    assert required.issubset(set(dir(FundingRateProvider)))
