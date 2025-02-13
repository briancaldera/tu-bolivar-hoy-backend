from peewee import Model, UUIDField, CharField, DateTimeField, DecimalField
import os
from playhouse.db_url import connect

database_url = os.getenv("DATABASE_URL")

db = connect(database_url)


class Currency(Model):
    id = UUIDField(primary_key=True)  # UUID7
    currency = CharField()  # e. g. USD
    datetime = DateTimeField()
    rate = DecimalField(max_digits=19, decimal_places=8, null=True)

    class Meta:
        table_name = "currencies"
        database = db
