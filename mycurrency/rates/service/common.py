from datetime import date, timedelta
from typing import List

from ..domain.db import get_exchange_rates_grouped_by_date_and_currency
from ..models import CurrencyExchangeRate


def get_missing_rate_dates(
    source_currency: str,
    date_from: date,
    date_to: date
) -> List[List[date]]:
    """
    Identify missing currency exchange rate dates within a specified date range.

    This function checks for missing exchange rate data for a given source currency
    between `date_from` and `date_to`. It returns a list of lists, where each sublist
    contains consecutive dates for which data is missing.

    Args:
        source_currency (str): The currency code for the source currency (e.g., 'USD').
        date_from (date): The start date of the range to check.
        date_to (date): The end date of the range to check.

    Returns:
        List[List[date]]: A list of lists, each containing consecutive missing dates.

    Raises:
        ValueError: If `date_from` is after `date_to`.

    Example:
        >>> get_missing_rate_dates('USD', date(2023, 1, 1), date(2023, 1, 10))
        [[datetime.date(2023, 1, 3), datetime.date(2023, 1, 4)],
         [datetime.date(2023, 1, 7)]]
    """
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
    response = []
    current_subset = [sorted_missing_dates[0]]

    # Identify subsets of consecutive dates
    for i in range(1, len(sorted_missing_dates)):
        if (sorted_missing_dates[i] - sorted_missing_dates[i - 1]).days == 1:
            current_subset.append(sorted_missing_dates[i])
        else:
            response.append(current_subset)
            current_subset = [sorted_missing_dates[i]]

    # Add the last subset
    response.append(current_subset)
    return response
