import locale
import os
from typing import Any

from firebase_admin import initialize_app, functions
from firebase_functions import https_fn, scheduler_fn, tasks_fn
from firebase_functions import logger
from firebase_functions.options import RetryConfig, RateLimits
from datetime import datetime, timedelta

from exchange_rate.functions import (
    check_integrity,
    fetch_exchange_rates,
    retrieve_exchange_rate_for_hours,
)
from utils.utils import get_function_url

locale_string: str = os.getenv("LOCALE")

locale.setlocale(locale.LC_ALL, locale_string)

initialize_app()


@scheduler_fn.on_schedule(schedule="every 1 hours synchronized")
def enqueue_fetch_exchange_rates(_: scheduler_fn.ScheduledEvent) -> None:
    logger.info("Enqueueing fetch_exchange_rates task")
    try:
        task_queue = functions.task_queue("taskfetchexchangerates")
        target_uri = get_function_url("taskfetchexchangerates")

        dispatch_deadline_seconds = 60 * 30

        task_options = functions.TaskOptions(
            dispatch_deadline_seconds=dispatch_deadline_seconds, uri=target_uri
        )

        now = datetime.now().isoformat()[:10]
        body = {"data": {"date": now}}

        task_queue.enqueue(body, task_options)
        logger.info("Task enqueued successfully")
    except Exception as e:
        logger.error(f"Error enqueuing task: {e}")
        raise


@tasks_fn.on_task_dispatched(
    retry_config=RetryConfig(max_attempts=10, min_backoff_seconds=60 * 3),
    rate_limits=RateLimits(max_concurrent_dispatches=1),
)
def taskfetchexchangerates(_: tasks_fn.CallableRequest) -> None:
    """
    This function is a scheduled function that runs every hour.
    It fetches the latest exchange rates and saves them to the database.
    """
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
