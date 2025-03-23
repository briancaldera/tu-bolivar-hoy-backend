from dataclasses import dataclass


@dataclass()
class ExchangeID:
    def __init__(self, exchange_id: str):
        self.value: str = exchange_id


@dataclass()
class Currency:
    def __init__(self, currency: str):

        if currency not in ["USD", "EUR", "TRY", "CNY", "RUB"]:
            raise Exception(f"Currency {currency} not valid", currency)

        self.value: str = currency


@dataclass()
class Rate:
    def __init__(self, rate: float):

        if rate < 0:
            raise Exception("Exchange rate cannot be negative")

        self.value: float = rate
