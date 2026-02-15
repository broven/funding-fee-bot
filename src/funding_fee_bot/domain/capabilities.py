from enum import Enum


class ProviderCapability(str, Enum):
    FUNDING_RATE = "funding_rate"
    SPOT_PRICE = "spot_price"
    ORDER_BOOK = "order_book"
