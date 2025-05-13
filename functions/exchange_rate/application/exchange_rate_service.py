from datetime import datetime, timedelta
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
import pytz


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

        for currency_name, rate_str in exchange_rates.items():
            currency = Currency(currency_name)
            timezone = pytz.timezone("America/Caracas")
            now = datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(
                hours=4
            )
            created_at = timezone.localize(now)
            rate = Rate(Decimal(rate_str))

            exchange_rate = ExchangeRate.create(None, currency, rate, created_at)
            data.append(exchange_rate)

        self._exchangeRepo.save_exchange_rates(data)
