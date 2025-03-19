from datetime import date, timedelta

from ..models import Currency, CurrencyExchangeRate
from ..adapters.adapter_factory import get_exchange_rate_data
from ..domain.db import get_exchange_rates_grouped_by_date_and_currency


def get_exchange_rates(
    source_currency: str,
    date_from: date,
    date_to: date
) -> list:

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
