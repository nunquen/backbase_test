from abc import ABC, abstractmethod
from datetime import date


class BaseExchangeRateAdapter(ABC):
    """
    Abstract base class for currency exchange rate providers.
    """

    @abstractmethod
    def get_exchange_rate_data(
        source_currency: str,
        exchanged_currency: str,
        date_from: date,
        date_to: date
    ) -> dict:
        """
        Fetch exchange rates from the provider.
        """
        pass
