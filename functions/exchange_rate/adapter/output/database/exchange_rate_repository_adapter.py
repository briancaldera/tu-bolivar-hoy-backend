from datetime import datetime
from typing import override

from exchange_rate.adapter.output.database.connection import db_wrapper
from exchange_rate.adapter.output.database.models.exchange_rate import (
    ExchangeRateAR,
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
                "registered_at": exchange_rate.registered_at,
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
                & (ExchangeRateAR.registered_at == time)
            )
            .get_or_none()
        )

        if exchange_rate is None:
            print(f"None value found for {time}")

        return exchange_rate.to_entity() if exchange_rate else None

    @override
    def get_exchange_rate_count_for_hour(self, time: datetime) -> int:
        count = (
            ExchangeRateAR.select().where(ExchangeRateAR.registered_at == time).count()
        )

        return count
