from datetime import date

from ..models import Currency, CurrencyExchangeRate
from mycurrency.rates.adapters.adapter_factory import get_exchange_rate_data


def get_exchange_rates(
    source_currency: str,
    date_from: date,
    date_to: date
) -> list:

    valid_currencies = set(Currency.objects.values_list("code", flat=True))

    # Removing source currency and getting the exchanged currencies
    exchanged_currencies = ",".join(valid_currencies - {source_currency})

    # exchange_rate, created = CurrencyExchangeRate.objects.get(
    #     source_currency=source_currency,
    #     exchanged_currency=exchanged_obj,
    #     valuation_date=valuation_date,
    #     defaults={"rate_value": rate_value},
    # )
    data = get_exchange_rate_data(
        source_currency=source_currency,
        exchanged_currency=exchanged_currencies,
        date_from=date_from,
        date_to=date_to
    )

    # Saving data in data base
    exchange_rate_list = []
    for date_rate, currency_data in data.items():
        for currency, rate in currency_data.items():
            source_currency_obj = Currency.objects.get(code=source_currency)
            exchanged_obj = Currency.objects.get(code=currency)

            exchange_rate, created = CurrencyExchangeRate.objects.get_or_create(
                source_currency=source_currency_obj,
                exchanged_currency=exchanged_obj,
                valuation_date=date_rate,
                defaults={"rate_value": rate},
            )
            exchange_rate_list.append({
                "source_currency": source_currency_obj,
                "exchanged_currency": exchanged_obj,
                "valuation_date": date_rate,
                "rate_value": rate,
            })

    return exchange_rate_list
