from playhouse.postgres_ext import (
    UUIDField,
    CharField,
    DateTimeTZField,
    DecimalField,
)

from exchange_rate.adapter.output.database.models.base_model import BaseModel


class ExchangeRateAR(BaseModel):
    id = UUIDField(primary_key=True)  # UUID7
    currency = CharField()  # e. g. USD
    datetime = DateTimeTZField()
    rate = DecimalField(max_digits=19, decimal_places=8, null=True)

    class Meta:
        table_name = "exchange_rates"
