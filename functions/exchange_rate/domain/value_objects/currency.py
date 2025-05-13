from dataclasses import dataclass


@dataclass()
class Currency:
    value: str

    def __post_init__(self):
        if self.value not in ("USD", "EUR", "TRY", "CNY", "RUB"):
            raise Exception(f"Currency {self.value} not valid", self.value)
