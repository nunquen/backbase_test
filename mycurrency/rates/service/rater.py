"""
This module provides services for retrieving exchange rates from the database
or fetching missing data from a remote provider when necessary.
It ensures complete data coverage for a specified date range by detecting and
filling gaps in exchange rate records.
"""
from datetime import date, datetime

from ..adapters.adapter_factory import (
    get_exchange_convertion_data,
    get_exchange_rate_data,
)
from .common import get_missing_rate_dates, save_data
from ..domain.db import get_exchange_rates_grouped_by_date_and_currency
from ..models import Currency, CurrencyExchangeRate


def get_exchange_rates(source_currency: str, date_from: date, date_to: date) -> list:
    """
    Retrieves exchange rates for a given source currency and date range.
    If all required data is available in the database, it is returned directly.
    Otherwise, missing data is fetched from a remote provider and stored.

    Args:
        source_currency (str): The currency code for the source currency (e.g., 'USD', 'EUR').
        date_from (date): The start date of the range for exchange rates.
        date_to (date): The end date of the range for exchange rates.

    Returns:
        list: A dictionary grouped by valuation date containing exchange rates
              for different currencies in the following structure:

              {
                  "YYYY-MM-DD": {
                      "source_currency/exchanged_currency": rate_value,
                      ...
                  },
                  ...
              }

    Raises:
        ValueError: If an invalid currency code is provided.
    """
    valid_currencies = set(Currency.objects.values_list("code", flat=True))

    # Removing source currency and getting the exchanged currencies
    exchanged_currencies = ",".join(valid_currencies - {source_currency})

    subsets = get_missing_rate_dates(
        source_currency=source_currency, date_from=date_from, date_to=date_to
    )

    # Fetching remote data
    data = {}
    for gap in subsets:
        new_data, _ = get_exchange_rate_data(
            source_currency=source_currency,
            exchanged_currency=exchanged_currencies,
            date_from=gap[0],
            date_to=gap[-1],
        )
        data.update(new_data)

    # Saving data in data base
    save_data(data=data, source_currency=source_currency)

    # Retrieving all data from database
    db_exchange_rates = get_exchange_rates_grouped_by_date_and_currency(
        source_currency=source_currency, date_from=date_from, date_to=date_to
    )
    return db_exchange_rates


def get_exchange_convertion(
    source_currency: str, exchanged_currency: str, amount: float
) -> dict:
    current_date = datetime.now().date()
    # Checking if we have to retrieve remote data
    db_rate = CurrencyExchangeRate.objects.filter(
        source_currency__code=source_currency,
        exchanged_currency__code=exchanged_currency,
        valuation_date=current_date,
    ).first()

    if db_rate:
        data = {
            "date": db_rate.valuation_date.strftime("%Y-%m-%d"),
            "source_currency": db_rate.source_currency.code,
            "exchanged_currency": db_rate.exchanged_currency.code,
            "amount": amount,
            "value": amount * db_rate.rate_value,
        }
        return data

    # We need to retrieve remote data
    data, _ = get_exchange_convertion_data(
        source_currency=source_currency,
        exchanged_currency=exchanged_currency,
        amount=amount,
    )
    data.pop("timestamp", None)  # Not showing timestamp

    # Saving new rate value in data base
    new_rate_value = data["value"] / float(amount)
    source_currency_obj = Currency.objects.get(code=source_currency)
    exchanged_obj = Currency.objects.get(code=exchanged_currency)

    CurrencyExchangeRate.objects.get_or_create(
        source_currency=source_currency_obj,
        exchanged_currency=exchanged_obj,
        valuation_date=current_date,
        defaults={"rate_value": new_rate_value},
    )

    return data
