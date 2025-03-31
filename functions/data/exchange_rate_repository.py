from abc import ABC, abstractmethod
from models.Currency import Currency
from valueobjects.valueobjects import Currency as CurrencyName
from datetime import datetime


class ExchangeRateRepository(ABC):

    @abstractmethod
    def get_exchange_rate_for_period(
        self, currency: CurrencyName, from_date: datetime, to_date: datetime
    ) -> list[Currency]:
        pass

    @abstractmethod
    def save_batch(self, exchange_rates: list[Currency]):
        pass
