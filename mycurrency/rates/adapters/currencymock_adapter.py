import random
from datetime import date, datetime, timedelta
from decimal import Decimal
from .base_adapter import BaseExchangeRateAdapter


class CurrencyMockAdapter(BaseExchangeRateAdapter):
    """
    Adapter to fetch mock exchange rates. This class simulates fetching exchange rates
    for a given date range or currency conversion.
    """

    def get_exchange_rate_data(
        source_currency: str,
        exchanged_currency: str,
        date_from: date,
        date_to: date
    ) -> dict:
        """
        Generate mock exchange rate data for a given date range.

        Args:
            source_currency (str): The source currency code (e.g., "USD").
            exchanged_currency (str): Comma-separated target currency codes (e.g., "EUR,GBP").
            date_from (date): The start date for the exchange rate data.
            date_to (date): The end date for the exchange rate data.

        Returns:
            dict: A dictionary where keys are date strings (YYYY-MM-DD), and values are
                  dictionaries mapping target currencies to their mock exchange rates.

        Raises:
            ValueError: If an error occurs while generating exchange rates.
        """
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

    def get_exchange_convertion_data(
        source_currency: str,
        exchanged_currency: str,
        amount: Decimal
    ) -> dict:
        """
        Generate mock exchange conversion data for a given currency pair and amount.

        Args:
            source_currency (str): The source currency code (e.g., "USD").
            exchanged_currency (str): The target currency code (e.g., "EUR").
            amount (Decimal): The amount to be converted.

        Returns:
            dict: A dictionary containing:
                - "timestamp": The current Unix timestamp.
                - "date": The current date in YYYY-MM-DD format.
                - "source_currency": The source currency code.
                - "exchanged_currency": The target currency code.
                - "amount": The amount being converted.
                - "value": The converted amount based on a mock exchange rate.

        Raises:
            ValueError: If an error occurs while generating the conversion rate.
        """
        try:
            data = {
                "timestamp": datetime.now().timestamp(),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "source_currency": source_currency,
                "exchanged_currency": exchanged_currency,
                "amount": amount,
                "value": round(random.uniform(0.5, 1.5), 8) * float(amount)
            }
            return data
        except Exception:
            raise ValueError("Convertion rate not found")
