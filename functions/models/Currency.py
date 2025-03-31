from datetime import datetime as dt

from peewee import (
    Model,
    UUIDField,
    CharField,
    DateTimeField,
    DecimalField,
)

from database.database import Database

db = Database.get_connection()



class Currency(Model):
    id = UUIDField(primary_key=True)  # UUID7
    currency = CharField()  # e. g. USD
    datetime = DateTimeField()
    rate = DecimalField(max_digits=19, decimal_places=8, null=True)

    class Meta:
        table_name = "currencies"
        database = db

    def to_dict(self):
        return {
            "id": self.id,
            "currency": self.currency,
            "datetime": dt(
                self.datetime.year,
                self.datetime.month,
                self.datetime.day,
                self.datetime.hour,
                self.datetime.minute,
                self.datetime.second,
            ).isoformat(),
            "rate": self.rate,
        }

