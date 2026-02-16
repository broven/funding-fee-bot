from decimal import Decimal

from funding_fee_bot.domain.capabilities import ProviderCapability
from funding_fee_bot.domain.models import (
    FundingRateCurrent,
    PerpPerpOpportunity,
    SpotPerpDirection,
    SpotPerpOpportunity,
)
from funding_fee_bot.service.market_data_service import MarketDataService


class OpportunityDiscoveryService:
    def __init__(self, market_data_service: MarketDataService | None = None):
        self._market_data_service = market_data_service or MarketDataService()

    def discover_perp_perp_opportunities(
        self,
        exchanges: list[str] | None = None,
        min_funding_rate_spread: Decimal = Decimal("0"),
        symbols: set[str] | None = None,
    ) -> list[PerpPerpOpportunity]:
        target_symbols = self._normalize_symbols(symbols)
        grouped: dict[str, list[FundingRateCurrent]] = {}

        for exchange in self._resolve_exchanges(exchanges):
            provider = self._market_data_service.get_provider(
                exchange,
                required_capability=ProviderCapability.FUNDING_RATE,
            )
            for funding in provider.fetch_current_all():
                canonical_symbol = self._canonical_symbol(funding.symbol)
                if target_symbols and canonical_symbol not in target_symbols:
                    continue
                grouped.setdefault(canonical_symbol, []).append(funding)

        opportunities: list[PerpPerpOpportunity] = []
        for symbol, rows in grouped.items():
            if len(rows) < 2:
                continue

            low = min(rows, key=lambda row: row.funding_rate)
            high = max(rows, key=lambda row: row.funding_rate)
            spread = high.funding_rate - low.funding_rate
            if spread < min_funding_rate_spread:
                continue

            opportunities.append(
                PerpPerpOpportunity(
                    symbol=symbol,
                    long_exchange=low.exchange,
                    long_symbol=low.symbol,
                    long_funding_rate=low.funding_rate,
                    short_exchange=high.exchange,
                    short_symbol=high.symbol,
                    short_funding_rate=high.funding_rate,
                    funding_rate_spread=spread,
                )
            )

        return sorted(
            opportunities,
            key=lambda opportunity: opportunity.funding_rate_spread,
            reverse=True,
        )

    def discover_spot_perp_opportunities(
        self,
        exchanges: list[str] | None = None,
        min_abs_funding_rate: Decimal = Decimal("0"),
        symbols: set[str] | None = None,
    ) -> list[SpotPerpOpportunity]:
        target_symbols = self._normalize_symbols(symbols)
        opportunities: list[SpotPerpOpportunity] = []

        for exchange in self._resolve_exchanges(exchanges):
            provider = self._market_data_service.get_provider(
                exchange,
                required_capability=ProviderCapability.FUNDING_RATE,
            )
            if not provider.supports(ProviderCapability.SPOT_PRICE):
                continue

            for funding in provider.fetch_current_all():
                symbol = self._canonical_symbol(funding.symbol)
                if target_symbols and symbol not in target_symbols:
                    continue

                edge = abs(funding.funding_rate)
                if edge < min_abs_funding_rate:
                    continue

                try:
                    spot_ticker = provider.fetch_spot_ticker(symbol)
                except Exception:
                    continue

                direction = (
                    SpotPerpDirection.LONG_SPOT_SHORT_PERP
                    if funding.funding_rate >= 0
                    else SpotPerpDirection.SHORT_SPOT_LONG_PERP
                )
                opportunities.append(
                    SpotPerpOpportunity(
                        symbol=symbol,
                        exchange=funding.exchange,
                        perp_symbol=funding.symbol,
                        funding_rate=funding.funding_rate,
                        direction=direction,
                        expected_funding_edge=edge,
                        spot_last=spot_ticker.last,
                    )
                )

        return sorted(
            opportunities,
            key=lambda opportunity: opportunity.expected_funding_edge,
            reverse=True,
        )

    def _resolve_exchanges(self, exchanges: list[str] | None) -> list[str]:
        if exchanges is not None:
            return exchanges
        return self._market_data_service.available_exchanges()

    @staticmethod
    def _canonical_symbol(symbol: str) -> str:
        return symbol.split(":")[0]

    def _normalize_symbols(self, symbols: set[str] | None) -> set[str] | None:
        if symbols is None:
            return None
        return {self._canonical_symbol(symbol) for symbol in symbols}
