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
from decimal import Decimal
import logging
from rates.models import Provider
from .currencybeacon_adapter import CurrencyBeaconAdapter
from .currencymock_adapter import CurrencyMockAdapter


logger = logging.getLogger(__name__)

PROVIDER_MAPPING = {
    "CurrencyBeacon": CurrencyBeaconAdapter,
    "MockProvider": CurrencyMockAdapter,
}


def get_provider() -> Provider:
    """
    Retrieve the relevant Provider for fetching exchange rate data.

    The fetched Provider will be the enabled provider with the lowest priority.

    Returns:
        Provider: provider database object.
    """
    provider = Provider.objects.filter(is_enabled=True).order_by("priority").first()
    if provider:
        logger.info(f"Provider {provider.name} has been selected")
    else:
        logger.warning("No Provider has been selected")
    return provider


def get_exchange_rate_data(
    source_currency: str, exchanged_currency: str, date_from: date, date_to: date
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
    provider = get_provider()
    if not provider:
        raise ValueError("No available providers.")

    adapter_class = PROVIDER_MAPPING.get(provider.name)

    if not adapter_class:
        logger.error(f"Provider {provider.name} is not supported.")
        raise ValueError(f"Provider {provider.name} is not supported.")

    try:
        # Instantiate the adapter class with the provider's key
        adapter_instance = adapter_class(api_key=provider.key)

        data = adapter_instance.get_exchange_rate_data(
            exchanged_currency=exchanged_currency,
            source_currency=source_currency,
            date_from=date_from,
            date_to=date_to,
        )
        return data, provider.name
    except Exception as e:
        raise e


def get_exchange_convertion_data(
    source_currency: str, exchanged_currency: str, amount: Decimal
) -> dict:
    provider = get_provider()
    adapter_class = PROVIDER_MAPPING.get(provider.name)

    if not adapter_class:
        logger.error(f"Provider {provider.name} is not supported.")
        raise ValueError(f"Provider {provider.name} is not supported.")

    try:
        # Instantiate the adapter class with the provider's key
        adapter_instance = adapter_class(api_key=provider.key)

        data = adapter_instance.get_exchange_convertion_data(
            source_currency=source_currency,
            exchanged_currency=exchanged_currency,
            amount=amount,
        )
        return data, provider.name
    except Exception as e:
        raise e
