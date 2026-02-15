class FundingProviderError(Exception):
    def __init__(
        self,
        exchange: str,
        operation: str,
        message: str,
        symbol: str | None = None,
        retryable: bool = False,
    ):
        super().__init__(message)
        self.exchange = exchange
        self.operation = operation
        self.symbol = symbol
        self.retryable = retryable


class FundingNetworkError(FundingProviderError):
    pass


class FundingRateLimitError(FundingProviderError):
    pass


class FundingSymbolNotFoundError(FundingProviderError):
    pass


class FundingDataError(FundingProviderError):
    pass
