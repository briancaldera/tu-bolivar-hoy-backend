from typing import Any
from datetime import datetime

from exchange_rate.adapter.output.database.connection import db_wrapper
from exchange_rate.adapter.output.database.exchange_rate_repository_adapter import (
    ExchangeRateRepositoryAdapter,
)
from exchange_rate.adapter.output.database.models.exchange_rate import ExchangeRateAR
from exchange_rate.application.exchange_rate_service import ExchangeRateService
from exchange_rate.application.integrity_service import IntegrityService
from exchange_rate.data.etl.source import extract_data
from exchange_rate.domain.models.exchange_rate import ExchangeRate


def fetch_exchange_rates() -> None:
    exchange_rate_repository = ExchangeRateRepositoryAdapter()
    exchange_rate_service = ExchangeRateService(exchange_rate_repository)

    currencies = extract_data()
    exchange_rate_service.save_exchange_rates(currencies)


def retrieve_exchange_rate_for_hours(currency: str, iso_hours: list[str]) -> Any:
    hours = [
        datetime.fromisoformat(iso_hour).replace(minute=0, second=0, microsecond=0)
        for iso_hour in iso_hours
    ]

    repo = ExchangeRateRepositoryAdapter()
    service = ExchangeRateService(repo)

    res = service.get_exchange_rate_for_hours(currency, hours)

    data = {}

    for hour, rate in res.items():
        data[hour] = exchange_rate_to_dict(rate)

    return data


def check_integrity():
    """
    This function is an integrity check.
    """

    # Perform the integrity check here
    # For example, you can check if the database is consistent or if there are any missing records
    # since 2025-02-20 00:00:00, there should be no missing records
    # each day should have 24 * 5 = 120 records
    # if any days fails this rule, we take note to find which hours are missing,
    # and then we can send a notification

    integrity_service = IntegrityService()
    integrity_service.check_integrity()

    # You can also send an email or a notification if the integrity check fails
    # For example, you can use Firebase Cloud Messaging to send a notification


def create_table():
    """
    This function creates the table in the database.
    """

    db = db_wrapper.database
    db.connect()
    db.create_tables([ExchangeRateAR])


# todo: move to a more appropriate place
def exchange_rate_to_dict(exchange: ExchangeRate | None):
    if exchange is None:
        return None

    return {
        "id": exchange.exchange_id.value,
        "currency": exchange.currency.value,
        "registered_at": exchange.registered_at.isoformat(),
        "rate": exchange.rate.value,
    }
