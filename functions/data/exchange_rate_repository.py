from abc import ABC, abstractmethod
from typing import override
from database.supabase_db import SupabaseDB, Database
from models.Currency import Currency
from valueobjects.valueobjects import Currency as CurrencyName
from datetime import datetime
import os

class ExchangeRateRepository(ABC):

    @abstractmethod
    def get_exchange_rate_for_period(
        self, currency: CurrencyName, from_date: datetime, to_date: datetime
    ) -> list[Currency]:
        pass

    @abstractmethod
    def save_batch(self, exchange_rates: list[Currency]):
        pass
