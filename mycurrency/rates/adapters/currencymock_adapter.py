import random
from datetime import date, timedelta
from django.conf import settings
from .base_adapter import BaseExchangeRateAdapter


class CurrencyMockAdapter(BaseExchangeRateAdapter):
    """
    Adapter to fetch exchange rates from CurrencyMock.
    """

    def get_currency_rates_list(
        source_currency: str,
        exchanged_currency: str,
        date_from: date,
        date_to: date
    ) -> dict:
        try:
            currencies = exchanged_currency.split(",")
            data = {}

            current_date = date_from
            while current_date <= date_to:
                data[current_date.strftime("%Y-%m-%d")] = {
                    currency: round(random.uniform(0.5, 1.5), 8) for currency in currencies
                }
                current_date += timedelta(days=1)

            return data
        except Exception:
            raise ValueError("Time Series rates not found")
