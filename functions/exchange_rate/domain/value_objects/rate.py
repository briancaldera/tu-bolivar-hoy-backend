from dataclasses import dataclass

@dataclass()
class Rate:
    value: float | None

    def __post_init__(self):
        if self.value is not None and self.value < 0:
            raise ValueError("Exchange rate cannot be negative")
