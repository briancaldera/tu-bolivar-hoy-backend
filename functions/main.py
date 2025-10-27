import locale
import os
from datetime import datetime
from decimal import Decimal
from typing import Any

from firebase_admin import initialize_app
from firebase_functions import https_fn, scheduler_fn, options, params, logger

from exchange_rate.data.etl.source import extract_data
from exchange_rate.domain.value_objects import Currency, Rate
from exchange_rate.functions import (
    check_integrity,
    fetch_exchange_rates,
    retrieve_exchange_rate_for_hours,
)

import json

SUPABASE_SECRET_KEY = params.SecretParam('SUPABASE_API_KEY')

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


@https_fn.on_request(service_account='supabase-service-account@tubolivarhoy.iam.gserviceaccount.com',secrets=[SUPABASE_SECRET_KEY],region='us-east4',cors=options.CorsOptions(cors_origins=[r'https://hwurcromdvurlylkviip.supabase.co'], cors_methods=['get']))
def get_last_currencies(req: https_fn.Request) -> https_fn.Response:

    if req.method != 'GET':
        return https_fn.Response('Method Not Allowed', status=405)

    received_key = req.headers.get('x-supabase-key')

    expected_key = SUPABASE_SECRET_KEY.value

    if not received_key or received_key != expected_key:
        logger.warn('Unauthorized access attempt to endpoint.')
        return https_fn.Response('Unauthorized', status=401)

    currencies = extract_data()

    retrieved_at = datetime.now()

    data = []

    for currency_name, rate_str in currencies.items():
        currency = Currency(currency_name)
        rate = Rate(Decimal(rate_str))

        exchange_rate = {
            'currency': currency.value,
            'rate': str(rate.value),
            'datetime': retrieved_at.isoformat()
        }
        data.append(exchange_rate)

    json_data = json.dumps({'currencies': data}),

    logger.info('Currencies fetched')
    logger.info(json_data)

    return https_fn.Response(
        json_data,
        content_type='application/json'
    )