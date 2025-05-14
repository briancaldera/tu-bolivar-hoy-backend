from dataclasses import dataclass
from uuid6 import uuid7


@dataclass()
class ExchangeID:
    value: uuid7
