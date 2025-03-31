from datetime import datetime

from valueobjects.valueobjects import ExchangeID, Currency, Rate


class ExchangeRate:
    def __init__(
        self,
        exchange_id: ExchangeID,
        currency: Currency,
        rate: Rate,
        created_at: datetime,
    ):
        self.id: ExchangeID = exchange_id
        self.currency: Currency = currency
        self.rate: Rate = rate
        self.created_at: datetime = created_at
