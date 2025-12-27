from datetime import datetime
from decimal import Decimal
from typing import override
from datetime import timedelta

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
from firebase_functions import logger


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
        # check if there are already exchange rates for the current hour
        # if so do not save the new exchange rates
        registered_at = datetime.now().replace(minute=0, second=0, microsecond=0)
        count = self._exchangeRepo.get_exchange_rate_count_for_hour(registered_at)

        if count > 0:
            logger.warn(f"Exchange rates already exist for {registered_at}")
            return

        data: list[ExchangeRate] = []

        for currency_name, rate_str in exchange_rates.items():
            currency = Currency(currency_name)
            rate = Rate(Decimal(rate_str))

            exchange_rate = ExchangeRate.create(currency, rate, registered_at)
            data.append(exchange_rate)

        logger.info("Saving exchange rates...")
        self._exchangeRepo.save_exchange_rates(data)
        logger.info("Exchange rates saved successfully")

    @override
    def error_condition(self) -> None:
        """
        This method is intended to be called when an error condition is detected,
        specifically when the scheduled job to save exchange rates fails.
        It attempts to retrieve the exchange rates from the previous hour
        and save them for the current hour.
        """

        previous_hour = datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)

        currencies = ["USD", "EUR", "RUB", "CNY", "TRY"]
        currency_dict: dict[str, str] = {}

        for currency in currencies:
            rate = self._exchangeRepo.get_exchange_rate_for_datetime(Currency(currency), previous_hour)

            if rate is None:
                logger.error(f"No exchange rate found for {currency} at {previous_hour}. Cannot recover from error.")
                raise Exception(f"No exchange rate found for {currency} at {previous_hour}. Cannot recover from error.")


            currency_dict[currency] = str(rate.rate.value)

        self.save_exchange_rates(currency_dict)
