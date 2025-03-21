"""
Adapter Factory for Fetching Exchange Rate Data

This module serves as an adapter factory that dynamically provides access 
to different exchange rate providers (e.g., "currencybeacon"). It maps 
provider names to their respective adapter classes and uses the 
appropriate adapter to retrieve exchange rate data for a specified 
source currency, exchanged currency, and date range.

The factory pattern allows for easy extension and addition of new providers 
without changing the core logic of the system. The provider used is determined 
dynamically at runtime.

Functions:
    get_provider: Returns the current provider for fetching exchange rate data.
    get_exchange_rate_data: Fetches exchange rate data from the configured provider.

Constants:
    PROVIDER_MAPPING (dict): A dictionary mapping provider names to their respective adapter classes.

Classes:
    CurrencyBeaconAdapter (Class): Adapter class to interface with the CurrencyBeacon provider.

Example:
    provider_name = get_provider()
    exchange_data = get_exchange_rate_data("USD", "EUR", date(2021, 1, 1), date(2021, 12, 31))

    This would use the current provider (e.g., "currencybeacon") to fetch exchange rate data.
"""
from datetime import date
from typing import Union
from .currencybeacon_adapter import CurrencyBeaconAdapter
from .currencymock_adapter import CurrencyMockAdapter
from decimal import Decimal


PROVIDER_MAPPING = {
    "currencybeacon": CurrencyBeaconAdapter,
    "currencymock": CurrencyMockAdapter
}


# TODO: have this from the database
def get_provider():
    """
    Retrieve the current provider for fetching exchange rate data.

    For now, this function returns a hardcoded provider ("currencybeacon").
    In the future, this can be dynamically fetched from a database or configuration.

    Returns:
        str: The name of the provider (currently hardcoded as "currencybeacon").
    """
    return "currencymock"


def get_exchange_rate_data(
    source_currency: str,
    exchanged_currency: str,
    date_from: date,
    date_to: date
) -> Union[dict, str]:
    """
    Fetch exchange rate data for a given source and exchanged currency within the specified date range.

    This function retrieves exchange rate data by using the configured provider (e.g., "currencybeacon").
    It will check if the provider is available and then use it to fetch the data. If no provider is found
    or an error occurs, an exception will be raised.

    Args:
        source_currency (str): The source currency code (e.g., "USD").
        exchanged_currency (str): The target currency code (e.g., "EUR").
        date_from (date): The start date for fetching exchange rates.
        date_to (date): The end date for fetching exchange rates.

    Returns:
        Union[dict, str]: A dictionary of exchange rate data retrieved from the provider and the provider name,
        or an error message if failed.

    Raises:
        ValueError: If the provider is not supported.
        Exception: If there is an error in fetching the exchange rate data from the provider.
    """
    provider_name = get_provider()
    adapter_class = PROVIDER_MAPPING.get(provider_name)

    if not adapter_class:
        raise ValueError(f"Provider {provider_name} is not supported.")

    try:
        data = adapter_class.get_exchange_rate_data(
            exchanged_currency=exchanged_currency,
            source_currency=source_currency,
            date_from=date_from,
            date_to=date_to
        )
        return data, provider_name
    except Exception as e:
        raise e


def get_exchange_convertion_data(
    source_currency: str,
    exchanged_currency: str,
    amount: Decimal
) -> dict:
    provider_name = get_provider()
    adapter_class = PROVIDER_MAPPING.get(provider_name)

    if not adapter_class:
        raise ValueError(f"Provider {provider_name} is not supported.")

    try:
        data = adapter_class.get_exchange_convertion_data(
            source_currency=source_currency,
            exchanged_currency=exchanged_currency,
            amount=amount
        )
        return data, provider_name
    except Exception as e:
        raise e
