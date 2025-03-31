from datetime import datetime, timedelta
import uuid6
from models.Currency import Currency
from utils.utils import get_db


def save_to_db(currencies: dict):

    time = datetime.now()
    tm = time - timedelta(
        minutes=time.minute, seconds=time.second, microseconds=time.microsecond
    )

    data = [
        {"id": uuid6.uuid7(), "currency": currency, "datetime": tm, "rate": rate}
        for currency, rate in currencies.items()
    ]

    db = get_db()
    db.connect(reuse_if_open=True)

    with db.atomic():
        Currency.insert_many(data).execute()
