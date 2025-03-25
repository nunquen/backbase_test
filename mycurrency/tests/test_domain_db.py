import pytest
from datetime import date
from rates.models import CurrencyExchangeRate
from rates.domain.db import get_exchange_rates_grouped_by_date_and_currency
from rest_framework.test import APIClient

from rates.models import BatchProcess, Currency


@pytest.fixture
def clear_db():
    """Clears the database before each test to avoid UNIQUE constraint errors."""
    BatchProcess.objects.all().delete()
    Currency.objects.all().delete()


@pytest.fixture
def api_client():
    """Fixture for the Django REST Framework API client."""
    return APIClient()


@pytest.fixture
def create_currencies():
    """Fixture to create test currencies in the database."""
    Currency.objects.get_or_create(code="USD", name="US Dollar", symbol="$")
    Currency.objects.get_or_create(code="EUR", name="Euro", symbol="€")
    Currency.objects.get_or_create(code="GBP", name="Pound Sterlin", symbol="£")


@pytest.mark.django_db
@pytest.mark.parametrize(
    "source, exchanged, date_from, date_to, valuation_date, rate_value, grouped_result, description",
    [
        (
            "USD",
            ["EUR", "GBP"],
            date(2025, 3, 1),
            date(2025, 3, 10),
            date(2025, 3, 5),
            1.1,
            {"2025-03-05": {"USD/EUR": 1.1, "USD/GBP": 1.1}},
            "Exchange rates",
        ),
    ],
)
def test_exchange_rates_grouping(
    clear_db,
    create_currencies,
    source,
    exchanged,
    date_from,
    date_to,
    valuation_date,
    rate_value,
    grouped_result,
    description,
):
    # Create test data
    source_currency_obj = Currency.objects.get(code=source)
    for exchanged_currency in exchanged:
        exchanged_obj = Currency.objects.get(code=exchanged_currency)
        CurrencyExchangeRate.objects.get_or_create(
            source_currency=source_currency_obj,
            exchanged_currency=exchanged_obj,
            valuation_date=valuation_date,
            rate_value=rate_value,
        )

    # Call the function
    result = get_exchange_rates_grouped_by_date_and_currency(
        source_currency=source, date_from=date_from, date_to=date_to
    )

    # Assert the results
    assert result == grouped_result, description
