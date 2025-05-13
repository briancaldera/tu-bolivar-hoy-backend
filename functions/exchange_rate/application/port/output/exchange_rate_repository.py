from abc import ABC, abstractmethod
from datetime import datetime

from exchange_rate.domain.models.exchange_rate import ExchangeRate
from exchange_rate.domain.value_objects import Currency


class ExchangeRateRepository(ABC):
    @abstractmethod
    def save_exchange_rates(self, exchange_rates: list[ExchangeRate]) -> None:
        pass

    @abstractmethod
    def get_exchange_rate_for_datetime(
        self, currency: Currency, time: datetime
    ) -> ExchangeRate | None:
        pass
