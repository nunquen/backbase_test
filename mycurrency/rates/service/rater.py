"""
This module provides services for retrieving exchange rates from the database 
or fetching missing data from a remote provider when necessary.
It ensures complete data coverage for a specified date range by detecting and 
filling gaps in exchange rate records.
"""
from datetime import date, datetime, timedelta

from ..models import Currency, CurrencyExchangeRate
from ..adapters.adapter_factory import get_exchange_rate_data, get_exchange_convertion_data
from ..domain.db import get_exchange_rates_grouped_by_date_and_currency


def get_exchange_rates(
    source_currency: str,
    date_from: date,
    date_to: date
) -> list:
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

    # Checking if we have to retrieve remote data
    date_range = {date_from + timedelta(days=i) for i in range((date_to - date_from).days + 1)}
    db_date_range = set(
        CurrencyExchangeRate.objects.filter(
            source_currency__code=source_currency,
            valuation_date__range=(date_from, date_to)
        ).values_list("valuation_date", flat=True)
    )
    # Identify missing dates
    missing_dates = date_range - db_date_range

    # Case 1: we have all data in the database
    if not missing_dates:
        db_exchange_rates = get_exchange_rates_grouped_by_date_and_currency(
            source_currency=source_currency,
            date_from=date_from,
            date_to=date_to
        )
        return db_exchange_rates

    # Case 2: we have missing dates so let's see if there're any gaps
    sorted_missing_dates = sorted(missing_dates)

    # Initialize variables to track subsets and gaps
    subsets = []
    current_subset = [sorted_missing_dates[0]]

    # Identify subsets of consecutive dates
    for i in range(1, len(sorted_missing_dates)):
        if (sorted_missing_dates[i] - sorted_missing_dates[i - 1]).days == 1:
            current_subset.append(sorted_missing_dates[i])
        else:
            subsets.append(current_subset)
            current_subset = [sorted_missing_dates[i]]

    # Add the last subset
    subsets.append(current_subset)

    # Fetching remote data
    data = {}
    provider = ""
    for gap in subsets:
        new_data, provider_name = get_exchange_rate_data(
            source_currency=source_currency,
            exchanged_currency=exchanged_currencies,
            date_from=gap[0],
            date_to=gap[-1]
        )
        data.update(new_data)
        provider = provider_name

    # Saving data in data base
    for date_rate, currency_data in data.items():
        for currency, rate in currency_data.items():
            source_currency_obj = Currency.objects.get(code=source_currency)
            exchanged_obj = Currency.objects.get(code=currency)

            CurrencyExchangeRate.objects.get_or_create(
                source_currency=source_currency_obj,
                exchanged_currency=exchanged_obj,
                valuation_date=date_rate,
                defaults={"rate_value": rate},
            )

    # Retrieving all data from database
    db_exchange_rates = get_exchange_rates_grouped_by_date_and_currency(
            source_currency=source_currency,
            date_from=date_from,
            date_to=date_to
        )
    return db_exchange_rates


def get_exchange_convertion(
    source_currency: str,
    exchanged_currency: str,
    amount: float
) -> dict:
    current_date = datetime.now().date()
    # Checking if we have to retrieve remote data
    db_rate = CurrencyExchangeRate.objects.filter(
            source_currency__code=source_currency,
            exchanged_currency__code=exchanged_currency,
            valuation_date=current_date
        ).first()

    if db_rate:
        data = {
            "date": db_rate.valuation_date.strftime("%Y-%m-%d"),
            "from": db_rate.source_currency.code,
            "to": db_rate.exchanged_currency.code,
            "amount": amount,
            "value": amount * db_rate.rate_value
        }
        return data

    # We need to retrieve remote data
    data, provider_name = get_exchange_convertion_data(
        source_currency=source_currency,
        exchanged_currency=exchanged_currency,
        amount=amount
    )

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
