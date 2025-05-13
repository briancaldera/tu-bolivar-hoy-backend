from dataclasses import dataclass
from decimal import Decimal


@dataclass()
class Rate:
    value: Decimal

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Exchange rate cannot be negative")
