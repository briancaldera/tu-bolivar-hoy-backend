import locale
import os
from datetime import datetime, timedelta

from firebase_admin import initialize_app, functions
from firebase_functions import https_fn, options, tasks_fn
from firebase_functions.options import RetryConfig
from flask import jsonify
from playhouse.db_url import connect

from db import save_to_db
from models.Currency import Currency
from source import get_source
from utils import get_function_url

locale_string: str = os.getenv("LOCALE")

locale.setlocale(locale.LC_ALL, locale_string)

initialize_app()


@https_fn.on_request(cors=options.CorsOptions(cors_origins="*", cors_methods=["get"]))
def update_currencies(req: https_fn.Request):
    currencies: dict = get_source()
    save_to_db(currencies)
    return https_fn.Response(status=200, response="OK")


@https_fn.on_request()
def enqueue_initialize_db(_: https_fn.Request) -> https_fn.Response:
    task_queue = functions.task_queue("initialize_db")
    target_uri = get_function_url("initialize_db")

    start_time = datetime.now() + timedelta(seconds=10)

    body = {"data": {"date": start_time.isoformat()[:10]}}

    task_options = functions.TaskOptions(schedule_time=start_time, uri=target_uri)

    task_queue.enqueue(body, task_options)
    return https_fn.Response(status=200, response="Enqueued")


@tasks_fn.on_task_dispatched(
    retry_config=RetryConfig(max_attempts=0),
)
def initialize_db(req: tasks_fn.CallableRequest) -> bool:
    database_url = os.getenv("DATABASE_URL")
    db = connect(database_url)
    db.connect()
    db.create_tables([Currency])
    return db.close()


@https_fn.on_request(cors=options.CorsOptions(cors_origins="*", cors_methods=["get"]))
def get_last_currencies(req: https_fn.Request) -> https_fn.Response:

    currencies_name = [
        "USD",
        "EUR",
        "RUB",
        "CNY",
        "TRY",
    ]

    currencies = []

    for i, v in enumerate(currencies_name):

        currency = (
            Currency.select(
                Currency.id, Currency.currency, Currency.rate, Currency.datetime
            )
            .where(Currency.currency == v)
            .order_by(Currency.datetime.desc())
            .limit(1)
            .first()
        )

        data = {
            "id": currency.id,
            "currency": currency.currency,
            "rate": currency.rate,
            "datetime": currency.datetime,
        }

        currencies.append(data)

    return jsonify(currencies)
