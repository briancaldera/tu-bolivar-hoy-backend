from datetime import datetime

from exchange_rate.domain.value_objects import ExchangeID, Currency, Rate
from uuid6 import uuid7


class ExchangeRate:
    def __init__(
        self,
        exchange_id: ExchangeID | None,
        currency: Currency,
        rate: Rate | None,
        registered_at: datetime,
    ):
        self.exchange_id: ExchangeID | None = exchange_id
        self.currency: Currency = currency
        self.rate: Rate | None = rate
        self.registered_at: datetime = registered_at

    @staticmethod
    def create(
        currency: Currency,
        rate: Rate | None,
        registered_at: datetime,
    ):
        exchange_id = ExchangeID(uuid7())
        return ExchangeRate(exchange_id, currency, rate, registered_at)
