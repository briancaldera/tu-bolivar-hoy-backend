from peewee import (
    Model,
    UUIDField,
    CharField,
    DateTimeField,
    DecimalField,
)
from utils.utils import get_db

db = get_db()


class Currency(Model):
    id = UUIDField(primary_key=True)  # UUID7
    currency = CharField()  # e. g. USD
    datetime = DateTimeField()
    rate = DecimalField(max_digits=19, decimal_places=8, null=True)

    class Meta:
        table_name = "currencies"
        database = db
