from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal


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

    @abstractmethod
    def get_exchange_convertion_data(
        source_currency: str,
        exchanged_currency: str,
        amount: Decimal
    ) -> dict:
        """
        Fetch exchange convertion from the provider.
        """
