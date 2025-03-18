import requests
from datetime import date
from django.conf import settings
from .base_adapter import BaseExchangeRateAdapter


class CurrencyBeaconAdapter(BaseExchangeRateAdapter):
    """
    Adapter to fetch exchange rates from CurrencyBeacon.
    """

    BASE_URL = "https://api.currencybeacon.com/v1"

    def get_currency_rates_list(
        source_currency: str,
        exchanged_currency: str,
        date_from: date,
        date_to: date
    ) -> dict:
        headers = {
            "Authorization": "Bearer {}".format(
                settings.CURRENCY_BEACON_API_KEY
            )
        }
        params = {
            "start_date": date_from.strftime("%Y-%m-%d"),
            "end_date": date_to.strftime("%Y-%m-%d"),
            "base": source_currency,
            "symbols": exchanged_currency
        }
        endpoint = "{}/timeseries".format(CurrencyBeaconAdapter.BASE_URL)
        response = requests.get(endpoint, params=params, headers=headers)

        if response.status_code != 200:
            raise ValueError(f"API request failed: {response.status_code} - {response.text}")  # noqa: E501

        data = response.json()

        if "response" in data:
            return data["response"]
        else:
            raise ValueError("Time Series rates not found")
