from decimal import Decimal

from funding_fee_bot.domain.capabilities import ProviderCapability
from funding_fee_bot.domain.models import FundingRateCurrent, SpotTicker
from funding_fee_bot.domain.models.opportunity import SpotPerpDirection
from funding_fee_bot.service.market_data_service import MarketDataService
from funding_fee_bot.service.opportunity_discovery_service import OpportunityDiscoveryService


def _funding(exchange: str, symbol: str, rate: str) -> FundingRateCurrent:
    return FundingRateCurrent(
        exchange=exchange,
        symbol=symbol,
        funding_rate=Decimal(rate),
        funding_timestamp=1700000000000,
        next_funding_timestamp=1700028800000,
        fetched_at=1700000001000,
    )


def _spot(exchange: str, symbol: str, last: str) -> SpotTicker:
    return SpotTicker(
        exchange=exchange,
        symbol=symbol,
        last=Decimal(last),
        bid=None,
        ask=None,
        timestamp=1700000000000,
        fetched_at=1700000001000,
    )


def _provider_cls(
    exchange: str,
    capabilities: set[ProviderCapability],
    funding_rows: list[FundingRateCurrent],
    spot_map: dict[str, SpotTicker] | None = None,
):
    class StubProvider:
        exchange_id = exchange
        capabilities: set[ProviderCapability] = set()

        def supports(self, capability: ProviderCapability) -> bool:
            return capability in self.capabilities

        def fetch_current_all(self) -> list[FundingRateCurrent]:
            return list(funding_rows)

        def fetch_spot_ticker(self, symbol: str) -> SpotTicker:
            if spot_map is None:
                raise KeyError(symbol)
            return spot_map[symbol]

    StubProvider.capabilities = capabilities
    return StubProvider


def test_discover_perp_perp_opportunities_uses_funding_spread():
    service = OpportunityDiscoveryService(
        market_data_service=MarketDataService(
            providers={
                "binance": _provider_cls(
                    exchange="binance",
                    capabilities={ProviderCapability.FUNDING_RATE},
                    funding_rows=[
                        _funding("binance", "BTC/USDT:USDT", "0.0005"),
                        _funding("binance", "ETH/USDT:USDT", "0.0001"),
                    ],
                ),
                "bybit": _provider_cls(
                    exchange="bybit",
                    capabilities={ProviderCapability.FUNDING_RATE},
                    funding_rows=[
                        _funding("bybit", "BTC/USDT:USDT", "-0.0002"),
                        _funding("bybit", "ETH/USDT:USDT", "0.0004"),
                    ],
                ),
            }
        )
    )

    opportunities = service.discover_perp_perp_opportunities(
        min_funding_rate_spread=Decimal("0.0004")
    )

    assert len(opportunities) == 1

    opportunity = opportunities[0]
    assert opportunity.symbol == "BTC/USDT"
    assert opportunity.long_exchange == "bybit"
    assert opportunity.short_exchange == "binance"
    assert opportunity.funding_rate_spread == Decimal("0.0007")


def test_discover_spot_perp_opportunities_infers_direction_and_filters_threshold():
    service = OpportunityDiscoveryService(
        market_data_service=MarketDataService(
            providers={
                "binance": _provider_cls(
                    exchange="binance",
                    capabilities={
                        ProviderCapability.FUNDING_RATE,
                        ProviderCapability.SPOT_PRICE,
                    },
                    funding_rows=[
                        _funding("binance", "BTC/USDT:USDT", "0.0006"),
                        _funding("binance", "ETH/USDT:USDT", "-0.0007"),
                        _funding("binance", "XRP/USDT:USDT", "0.0001"),
                    ],
                    spot_map={
                        "BTC/USDT": _spot("binance", "BTC/USDT", "50000"),
                        "ETH/USDT": _spot("binance", "ETH/USDT", "3000"),
                    },
                ),
                "bitget": _provider_cls(
                    exchange="bitget",
                    capabilities={ProviderCapability.FUNDING_RATE},
                    funding_rows=[_funding("bitget", "SOL/USDT:USDT", "0.0012")],
                ),
            }
        )
    )

    opportunities = service.discover_spot_perp_opportunities(
        min_abs_funding_rate=Decimal("0.0005")
    )

    assert len(opportunities) == 2

    top = opportunities[0]
    assert top.symbol == "ETH/USDT"
    assert top.direction == SpotPerpDirection.SHORT_SPOT_LONG_PERP
    assert top.expected_funding_edge == Decimal("0.0007")
    assert top.spot_last == Decimal("3000")

    second = opportunities[1]
    assert second.symbol == "BTC/USDT"
    assert second.direction == SpotPerpDirection.LONG_SPOT_SHORT_PERP
    assert second.expected_funding_edge == Decimal("0.0006")
