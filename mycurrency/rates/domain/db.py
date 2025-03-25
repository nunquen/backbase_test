"""
This module contains functions to fetch and group exchange rates from the database.
"""
from collections import defaultdict
from datetime import date

from ..models import CurrencyExchangeRate


def get_exchange_rates_grouped_by_date_and_currency(
    source_currency: str, date_from: date, date_to: date
) -> dict:
    """
    Fetches exchange rates from the database, filters them by source currency
    and a given date range, and groups the results by valuation date and currency pair.
    The data is returned as a dictionary.

    Args:
        source_currency (str): The currency code for the source currency
            (e.g., 'USD', 'EUR').
        date_from (date): The start date for the range to fetch exchange rates.
        date_to (date): The end date for the range to fetch exchange rates.

    Returns:
        dict: A dictionary with the following structure:
            {
                "valuation_date": {
                    "source_currency/exchanged_currency": rate_value,
                    ...
                },
                ...
            }
        Example:
            {
                "2025-03-10": {
                    "USD/GBP": 0.84188273,
                    "USD/EUR": 1.08509501
                },
                "2025-03-11": {
                    "USD/GBP": 0.84315884,
                    "USD/EUR": 1.08970418
                }
            }

    """
    # Getting CurrencyExchangeRate by source_currency and valuation_date range
    exchange_rate_queryset = (
        CurrencyExchangeRate.objects.filter(
            source_currency__code=source_currency,
            valuation_date__range=(date_from, date_to),
        )
        .select_related("exchanged_currency")
        .order_by("valuation_date", "exchanged_currency__code")
    )

    # Prepare a dictionary to store the results
    response = defaultdict(dict)
    for exchange_rate in exchange_rate_queryset:
        valuation_date = exchange_rate.valuation_date
        exchanged_currency_code = exchange_rate.exchanged_currency.code
        rate_value = exchange_rate.rate_value

        # Add the exchange rate for each currency under the corresponding valuation_date
        pair = "{}/{}".format(source_currency, exchanged_currency_code)
        response[valuation_date.strftime("%Y-%m-%d")][pair] = float(rate_value)

    return response
