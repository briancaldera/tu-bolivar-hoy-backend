from playhouse.postgres_ext import (
    UUIDField,
    CharField,
    DateTimeTZField,
    DecimalField,
)

from exchange_rate.adapter.output.database.models.base_model import BaseModel
from exchange_rate.domain.models.exchange_rate import ExchangeRate
from exchange_rate.domain.value_objects import ExchangeID, Currency, Rate


class ExchangeRateAR(BaseModel):
    id = UUIDField(primary_key=True)  # UUID7
    currency = CharField()  # e. g. USD
    registered_at = DateTimeTZField()
    rate = DecimalField(max_digits=19, decimal_places=8, null=True)

    class Meta:
        table_name = "exchange_rates"

    def to_entity(self) -> ExchangeRate:
        exchange_rate_id = ExchangeID(self.id)
        currency = Currency(self.currency)
        rate = Rate(self.rate)
        registered_at = self.registered_at
        return ExchangeRate(exchange_rate_id, currency, rate, registered_at)
