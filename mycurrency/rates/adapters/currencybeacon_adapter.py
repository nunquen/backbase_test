import logging
import json
from datetime import date
from decimal import Decimal
import requests

from .base_adapter import BaseExchangeRateAdapter


logger = logging.getLogger(__name__)


class CurrencyBeaconAdapter(BaseExchangeRateAdapter):
    """
    Adapter to fetch exchange rates from CurrencyBeacon.

    This adapter interacts with the CurrencyBeacon API to retrieve historical
    exchange rate data and perform currency conversions.
    """

    BASE_URL = "https://api.currencybeacon.com/v1"

    def __init__(self, api_key: str):
        super().__init__(api_key)

    def get_exchange_rate_data(
        self,
        source_currency: str,
        exchanged_currency: str,
        date_from: date,
        date_to: date,
    ) -> dict:
        """
        Fetch historical exchange rates from CurrencyBeacon API for a given date range.

        Args:
            source_currency (str): The base currency code (e.g., "USD").
            exchanged_currency (str): Comma-separated target currency codes (e.g., "EUR,GBP").
            date_from (date): The start date for retrieving exchange rate data.
            date_to (date): The end date for retrieving exchange rate data.

        Returns:
            dict: A dictionary containing exchange rates for each date in the range.

        Raises:
            ValueError: If the API request fails or the response does not contain expected data.
        """
        try:
            headers = {"Authorization": "Bearer {}".format(self.api_key)}
            params = {
                "start_date": date_from.strftime("%Y-%m-%d"),
                "end_date": date_to.strftime("%Y-%m-%d"),
                "base": source_currency,
                "symbols": exchanged_currency,
            }
            endpoint = "{}/timeseries".format(CurrencyBeaconAdapter.BASE_URL)
            response = requests.get(endpoint, params=params, headers=headers)

            if response.status_code != 200:
                msg = json.loads(response.text)["meta"]["error_detail"]
                error_msg = (
                    f"API request failed: {response.status_code} - {msg}"  # noqa: E501
                )
                logger.error(error_msg)
                raise ValueError(error_msg)

            data = response.json()

            if "response" in data:
                return data["response"]

            raise ValueError("Time Series rates not found")
        except Exception as e:
            raise e

    def get_exchange_convertion_data(
        self, source_currency: str, exchanged_currency: str, amount: Decimal
    ) -> dict:
        """
        Fetch real-time currency conversion data from CurrencyBeacon API.

        Args:
            source_currency (str): The base currency code (e.g., "USD").
            exchanged_currency (str): The target currency code (e.g., "EUR").
            amount (Decimal): The amount to be converted.

        Returns:
            dict: A dictionary containing:
                - "timestamp": The Unix timestamp of the conversion.
                - "date": The date of the conversion.
                - "source_currency": The source currency code.
                - "exchanged_currency": The target currency code.
                - "amount": The amount being converted.
                - "value": The converted amount.

        Raises:
            ValueError: If the API request fails or the response does not contain expected data.
        """
        try:
            error_msg = ""
            headers = {"Authorization": "Bearer {}".format(self.api_key)}
            params = {
                "from": source_currency,
                "to": exchanged_currency,
                "amount": amount,
            }
            endpoint = "{}/convert".format(CurrencyBeaconAdapter.BASE_URL)
            response = requests.get(endpoint, params=params, headers=headers)

            if response.status_code != 200:
                msg = json.loads(response.text)["meta"]["error_detail"]
                error_msg = (
                    f"API request failed: {response.status_code} - {msg}"  # noqa: E501
                )
                logger.error(error_msg)
                raise ValueError(error_msg)

            data = response.json()

            if "response" in data:
                parsed_data = {
                    "timestamp": data["response"]["timestamp"],
                    "date": data["response"]["date"],
                    "source_currency": data["response"]["from"],
                    "exchanged_currency": data["response"]["to"],
                    "amount": data["response"]["amount"],
                    "value": data["response"]["value"],
                }
                return parsed_data

            raise ValueError("Time Series rates not found")

        except Exception as e:
            raise ValueError(e)
