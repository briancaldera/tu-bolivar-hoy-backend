from datetime import datetime, timedelta

from data.exchange_rate_repository_impl import ExchangeRateRepoImpl
from models.Currency import Currency
from valueobjects.valueobjects import Currency as CurrencyName


class ExchangeRateService:
    def __init__(self):
        self._exchangeRepo = ExchangeRateRepoImpl()

    def exchange_for_day(self, currency: str, date: str) -> list[Currency]:

        date = datetime.fromisoformat(date)
        day = datetime(year=date.year, month=date.month, day=date.day)
        day_end = day + timedelta(days=1)

        currency = CurrencyName(currency)

        return self._exchangeRepo.get_exchange_rate_for_period(currency, day, day_end)

    def exchange_for_hours(self, currency_name: str, hours: list[datetime]) -> dict[str, Currency | None]:

        currency = CurrencyName(currency_name)

        result: dict[str, Currency | None] = {}

        for time in hours:
            rate = self._exchangeRepo.get_exchange_rate_for_datetime(currency, time)
            result[time.__str__()] = rate

        return result
