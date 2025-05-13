from datetime import datetime
from typing import override

from exchange_rate.adapter.output.database.connection import db_wrapper
from exchange_rate.adapter.output.database.models.exchange_rate import (
    ExchangeRate as ExchangeRateAR,
)
from exchange_rate.application.port.output.exchange_rate_repository import (
    ExchangeRateRepository,
)
from exchange_rate.domain.models.exchange_rate import ExchangeRate
from exchange_rate.domain.value_objects import Currency


class ExchangeRateRepositoryAdapter(ExchangeRateRepository):
    @override
    def save_exchange_rates(self, exchange_rates: list[ExchangeRate]) -> None:
        data = [
            {
                "id": exchange_rate.exchange_id.value,
                "currency": exchange_rate.currency.value,
                "datetime": exchange_rate.created_at,
                "rate": exchange_rate.rate.value,
            }
            for exchange_rate in exchange_rates
        ]

        with db_wrapper.database.atomic():
            ExchangeRateAR.insert_many(data).execute()

    @override
    def get_exchange_rate_for_datetime(
        self, currency: Currency, time: datetime
    ) -> ExchangeRate | None:
        exchange_rate = (
            ExchangeRateAR.select()
            .where(
                (ExchangeRateAR.currency == currency.value)
                & (ExchangeRateAR.datetime == time)
            )
            .get_or_none()
        )

        if exchange_rate is None:
            print(f"None value found for {time}")

        return exchange_rate
