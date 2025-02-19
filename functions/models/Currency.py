import os

from peewee import (
    Model,
    UUIDField,
    CharField,
    DateTimeField,
    DecimalField,
    PostgresqlDatabase,
)

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


class Currency(Model):
    id = UUIDField(primary_key=True)  # UUID7
    currency = CharField()  # e. g. USD
    datetime = DateTimeField()
    rate = DecimalField(max_digits=19, decimal_places=8, null=True)

    class Meta:
        table_name = "currencies"
        database = db
