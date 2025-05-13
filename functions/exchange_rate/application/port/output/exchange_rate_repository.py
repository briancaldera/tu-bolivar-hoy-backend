from abc import ABC, abstractmethod

from exchange_rate.domain.models.exchange_rate import ExchangeRate


class ExchangeRateRepository(ABC):
    @abstractmethod
    def save_exchange_rates(self, exchange_rates: list[ExchangeRate]) -> None:
        pass
