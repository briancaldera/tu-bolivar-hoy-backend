import locale
from datetime import datetime, timedelta
import uuid6

from models.Currency import Currency


def save_to_db(currencies: dict):

    time = datetime.now()
    tm = time - timedelta(
        minutes=time.minute, seconds=time.second, microseconds=time.microsecond
    )

    for x, y in currencies.items():
        uuid = uuid6.uuid7()
        currency = Currency.create(
            id=uuid, currency=x, datetime=tm, rate=locale.atof(y)
        )
