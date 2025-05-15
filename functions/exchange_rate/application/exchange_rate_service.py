from datetime import datetime
from decimal import Decimal
from typing import override

from exchange_rate.application.port.input.get_exchange_rate_for_hours_use_case import (
    GetExchangeRateForHoursUseCase,
)
from exchange_rate.application.port.input.save_exchange_rates_use_case import (
    SaveExchangeRatesUseCase,
)
from exchange_rate.application.port.output.exchange_rate_repository import (
    ExchangeRateRepository,
)
from exchange_rate.domain.models.exchange_rate import ExchangeRate
from exchange_rate.domain.value_objects import Currency, Rate


class ExchangeRateService(GetExchangeRateForHoursUseCase, SaveExchangeRatesUseCase):
    def __init__(self, exchange_repo: ExchangeRateRepository):
        self._exchangeRepo: ExchangeRateRepository = exchange_repo

    @override
    def get_exchange_rate_for_hours(
        self, currency_name: str, hours: list[datetime]
    ) -> dict[str, ExchangeRate | None]:
        currency = Currency(currency_name)

        result = {}

        for time in hours:
            rate = self._exchangeRepo.get_exchange_rate_for_datetime(currency, time)
            result[time.__str__()] = rate

        return result

    @override
    def save_exchange_rates(self, exchange_rates: dict[str, str]) -> None:
        data: list[ExchangeRate] = []

        registered_at = datetime.now().replace(minute=0, second=0, microsecond=0)

        for currency_name, rate_str in exchange_rates.items():
            currency = Currency(currency_name)
            rate = Rate(Decimal(rate_str))

            exchange_rate = ExchangeRate.create(currency, rate, registered_at)
            data.append(exchange_rate)

        self._exchangeRepo.save_exchange_rates(data)
