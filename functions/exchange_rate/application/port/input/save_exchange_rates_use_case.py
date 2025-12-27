from abc import ABC, abstractmethod


class SaveExchangeRatesUseCase(ABC):
    @abstractmethod
    def save_exchange_rates(self, exchange_rates: dict[str, str]) -> None:
        pass

    @abstractmethod
    def error_condition(self) -> None:
        pass
