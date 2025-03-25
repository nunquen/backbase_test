from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal


class BaseExchangeRateAdapter(ABC):
    """
    Abstract base class for currency exchange rate providers.
    This class includes an `api_key` to be used by subclasses to authenticate API requests.
    """

    def __init__(self, api_key: str):
        """
        Initializes the adapter with the provider's API key.

        Args:
            api_key (str): The API key to authenticate requests to the provider.
        """
        self.api_key = api_key

    @abstractmethod
    def get_exchange_rate_data(
        self,
        source_currency: str,
        exchanged_currency: str,
        date_from: date,
        date_to: date,
    ) -> dict:
        """
        Fetch exchange rates from the provider.
        """

    @abstractmethod
    def get_exchange_convertion_data(
        self, source_currency: str, exchanged_currency: str, amount: Decimal
    ) -> dict:
        """
        Fetch exchange convertion from the provider.
        """
