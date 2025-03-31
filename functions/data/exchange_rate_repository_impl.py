import os
from datetime import datetime
from typing import override

from assets.example_data import data
from data.exchange_rate_repository import ExchangeRateRepository
from database.database import Database
from models.Currency import Currency
from valueobjects.valueobjects import Currency as CurrencyName


class ExchangeRateRepoImpl(ExchangeRateRepository):

    def __init__(self):
        if os.getenv("APP_MODE") == "dev":

            conn = Database.get_connection()

            with conn.atomic():
                try:
                    conn.create_tables([Currency])
                    Currency.insert_many(data).execute()
                    conn.commit()

                except Exception as e:
                    print(e)
                    conn.rollback()

    @override
    def get_exchange_rate_for_period(
        self, currency: CurrencyName, from_date: datetime, to_date: datetime
    ) -> list[Currency]:

        exchange_rate_list: list[Currency] = (
            Currency.select()
            .where(
                (Currency.currency == currency.value)
                & (Currency.datetime >= from_date)
                & (Currency.datetime <= to_date)
            )
            .order_by(Currency.datetime.asc())
        )

        return exchange_rate_list

    @override
    def save_batch(self, exchange_rates: list[Currency]):

        with Database.get_connection().atomic():
            Currency.bulk_create(exchange_rates)
