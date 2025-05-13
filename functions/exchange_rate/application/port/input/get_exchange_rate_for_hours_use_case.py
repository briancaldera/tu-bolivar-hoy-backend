from abc import ABC, abstractmethod
from datetime import datetime

from exchange_rate.domain.models.exchange_rate import ExchangeRate


class GetExchangeRateForHoursUseCase(ABC):
    @abstractmethod
    def get_exchange_rate_for_hours(
        self, currency_name: str, hours: list[datetime]
    ) -> dict[str, ExchangeRate | None]:
        pass
