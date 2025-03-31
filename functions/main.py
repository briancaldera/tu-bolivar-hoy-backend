import locale
import os
from datetime import datetime, timedelta
from typing import Any

from firebase_admin import initialize_app, functions
from firebase_functions import https_fn, options, tasks_fn, scheduler_fn
from firebase_functions.options import RetryConfig
from flask import Flask, jsonify
from peewee import PostgresqlDatabase

from data.source import get_source
from database.db import save_to_db
from models.Currency import Currency
from services.exchange_rate_service import ExchangeRateService

from utils.utils import get_function_url, close_db

app = Flask(__name__)


@app.teardown_request
def _db_close(exc) -> None:
    close_db()


locale_string: str = os.getenv("LOCALE")

locale.setlocale(locale.LC_ALL, locale_string)

initialize_app()


@scheduler_fn.on_schedule(schedule="every 1 hours synchronized")
def update_currencies(_: scheduler_fn.ScheduledEvent) -> None:
    currencies: dict = get_source()
    save_to_db(currencies)


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
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")

    db = PostgresqlDatabase(
        db_name,
        host=db_host,
        user=db_user,
        password=db_password,
        port=db_port,
    )

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


@https_fn.on_call()
def get_exchange_rate_for_day(req: https_fn.CallableRequest) -> Any:
    service = ExchangeRateService()

    currency = req.data['currency']
    day = req.data['date']

    exchange_list = service.exchange_for_day(currency, day)

    data = []

    for exchange in exchange_list:
        data.append(exchange.to_dict())

    return {
        'exchange_rate': data
    }

@https_fn.on_call()
def test(_req: https_fn.CallableRequest) ->  Any:

    return {'message': "OK Greetings from the emulators!"}
