from datetime import date
from .currencybeacon_adapter import CurrencyBeaconAdapter

PROVIDER_MAPPING = {
    "currencybeacon": CurrencyBeaconAdapter,
}


# TODO: have this from the database
def get_provider():
    return "currencybeacon"


def get_exchange_rate_data(
    source_currency: str,
    exchanged_currency: str,
    date_from: date,
    date_to: date
) -> dict:
    provider_name = get_provider()
    adapter_class = PROVIDER_MAPPING.get(provider_name)

    if not adapter_class:
        raise ValueError(f"Provider {provider_name} is not supported.")

    try:
        #adapter = adapter_class()
        data = adapter_class.get_currency_rates_list(
            exchanged_currency=exchanged_currency,
            source_currency=source_currency,
            date_from=date_from,
            date_to=date_to
        )
        return data
    except Exception as e:
        raise e
