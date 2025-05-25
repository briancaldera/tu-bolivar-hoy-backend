import locale
import os
from typing import Any

from firebase_admin import initialize_app
from firebase_functions import https_fn, scheduler_fn

from exchange_rate.functions import (
    check_integrity,
    fetch_exchange_rates,
    retrieve_exchange_rate_for_hours,
)

locale_string: str = os.getenv("LOCALE")

locale.setlocale(locale.LC_ALL, locale_string)

initialize_app()


@scheduler_fn.on_schedule(
    schedule="every 1 hours synchronized",
    retry_count=5,
    min_backoff_seconds=180,
    max_retry_seconds=20 * 60,
)
def enqueue_fetch_exchange_rates(_: scheduler_fn.ScheduledEvent) -> None:
    fetch_exchange_rates()


@https_fn.on_call()
def get_exchange_rate_for_hours(req: https_fn.CallableRequest) -> Any:
    currency = req.data["currency"]
    iso_hours = req.data["hours"]

    res = retrieve_exchange_rate_for_hours(currency, iso_hours)

    return {"exchange_rate_map": res}


@scheduler_fn.on_schedule(schedule="every day 00:00")
def integrity_check(_: scheduler_fn.ScheduledEvent) -> None:
    check_integrity()
