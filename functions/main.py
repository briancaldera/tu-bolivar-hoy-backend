import locale
import os
from datetime import datetime
from typing import Any

from firebase_admin import initialize_app
from firebase_functions import https_fn, scheduler_fn
from flask import Flask

from data.source import get_source
from database.database import Database
from database.db import save_to_db
from services.exchange_rate_service import ExchangeRateService
from utils.utils import close_db

app = Flask(__name__)


@app.teardown_request
def _db_close(exc) -> None:
    close_db()
    Database.close_db()


locale_string: str = os.getenv("LOCALE")

locale.setlocale(locale.LC_ALL, locale_string)

initialize_app()


@scheduler_fn.on_schedule(schedule="every 1 hours synchronized")
def update_currencies(_: scheduler_fn.ScheduledEvent) -> None:
    currencies: dict = get_source()
    save_to_db(currencies)


@https_fn.on_call()
def get_exchange_rate_for_day(req: https_fn.CallableRequest) -> Any:
    service = ExchangeRateService()

    currency = req.data["currency"]
    day = req.data["date"]

    exchange_list = service.exchange_for_day(currency, day)

    data = []

    for exchange in exchange_list:
        data.append(exchange.to_dict())

    return {"exchange_rate": data}


@https_fn.on_call()
def get_exchange_rate_for_hours(req: https_fn.CallableRequest) -> Any:
    service = ExchangeRateService()

    iso_hours = req.data["hours"]

    currency = req.data["currency"]

    hours = []

    for iso_hour in iso_hours:
        hour = datetime.fromisoformat(iso_hour)
        filtered_hour = datetime(
            year=hour.year, month=hour.month, day=hour.day, hour=hour.hour
        )
        hours.append(filtered_hour)

    res = service.exchange_for_hours(currency, hours)

    data = {}

    for hour, rate in res.items():
        if rate is not None:
            data[hour] = rate.to_dict()
        else:
            data[hour] = rate

    return {"exchange_rate_map": data}

@scheduler_fn.on_schedule(schedule="every 1 days synchronized")
def integrity_check():
    """
    This function is a placeholder for the integrity check.
    It will be triggered every day at 00:00 UTC.
    """

    # Perform the integrity check here
    # For example, you can check if the database is consistent or if there are any missing records
    print("Performing integrity check...")
    # since 2025-02-20 00:00:00, there should be no missing records
    # each day should have 24 * 5 = 120 records
    # if any days fails this rule, we take note to find which hours are missing
    # and then we can send a notification


    # You can also send an email or a notification if the integrity check fails
    # For example, you can use Firebase Cloud Messaging to send a notification
    print("Integrity check completed.")

@https_fn.on_call()
def test(_req: https_fn.CallableRequest) -> Any:

    return {"message": "OK Greetings from the emulators!"}
