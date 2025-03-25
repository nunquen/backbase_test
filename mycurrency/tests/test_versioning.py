import pytest
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch

from rates.models import Currency


@pytest.fixture
def clear_db():
    """Clears the database before each test to avoid UNIQUE constraint errors."""
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


@pytest.mark.django_db
@pytest.mark.parametrize(
    "version, endpoint, status_code, method, patch_function, patch_return_value, params, description",
    [
        (
            "v1",
            "currency-rates",
            status.HTTP_200_OK,
            "GET",
            "rates.views.get_exchange_rates",
            {"2025-03-10": {"USD/EUR": 1.085}},
            {
                "source_currency": "EUR",
                "date_from": "2025-03-15",
                "date_to": "2025-03-15",
            },
            "> Validating: Currency rates v1",
        ),
        (
            "v2",
            "currency-rates",
            status.HTTP_200_OK,
            "GET",
            "rates.views.get_exchange_rates",
            {"2025-03-10": {"USD/EUR": 1.085}},
            {
                "source_currency": "EUR",
                "date_from": "2025-03-15",
                "date_to": "2025-03-15",
            },
            "> Validating: Currency rates v2",
        ),
        (
            "v3",
            "currency-rates",
            None,
            "GET",
            "rates.views.get_exchange_rates",
            {"2025-03-10": {"USD/EUR": 1.085}},
            {
                "source_currency": "EUR",
                "date_from": "2025-03-15",
                "date_to": "2025-03-15",
            },
            "> Validating: Exception on Currency rates v3",
        ),
        (
            "v1",
            "currency-converter",
            status.HTTP_200_OK,
            "GET",
            "rates.views.get_exchange_convertion",
            {
                "date": "2025-03-20",
                "from": "USD",
                "to": "EUR",
                "amount": 1.0,
                "value": 1.221674,
            },
            {"source_currency": "USD", "exchanged_currency": "EUR", "amount": 1.0},
            "> Validating: Currency converter v1",
        ),
        (
            "v2",
            "currency-converter",
            status.HTTP_200_OK,
            "GET",
            "rates.views.get_exchange_convertion",
            {
                "date": "2025-03-20",
                "from": "USD",
                "to": "EUR",
                "amount": 1.0,
                "value": 1.221674,
            },
            {"source_currency": "USD", "exchanged_currency": "EUR", "amount": 1.0},
            "> Validating: Currency converter v2",
        ),
        (
            "v3",
            "currency-converter",
            None,
            "GET",
            "rates.views.get_exchange_convertion",
            {
                "date": "2025-03-20",
                "from": "USD",
                "to": "EUR",
                "amount": 1.0,
                "value": 1.221674,
            },
            {"source_currency": "USD", "exchanged_currency": "EUR", "amount": 1.0},
            "> Validating: Exception on Currency converter v3",
        ),
        (
            "v2",
            "currency-history-rates",
            status.HTTP_200_OK,
            "POST",
            "rates.views.batch_process",
            {"process_id": "3b6b9a3d-7136-4e82-8229-49ac686f7466"},
            {
                "source_currency": "USD",
                "date_from": "2024-11-29",
                "date_to": "2024-12-21",
            },
            "> Validating: Currency history rates v2",
        ),
        (
            "v1",
            "currency-history-rates",
            None,
            "POST",
            "rates.views.batch_process",
            {"process_id": "3b6b9a3d-7136-4e82-8229-49ac686f7466"},
            {
                "source_currency": "USD",
                "date_from": "2024-11-29",
                "date_to": "2024-12-21",
            },
            "> Validating: Exception on Currency history rates v1",
        ),
    ],
)
def test_endpoints_versioning(
    version,
    endpoint,
    status_code,
    method,
    patch_function,
    patch_return_value,
    params,
    description,
    clear_db,
    api_client,
    create_currencies,
):
    with patch(
        patch_function, return_value=patch_return_value
    ) as mock_get_exchange_rates:
        try:
            url = reverse(
                endpoint, kwargs={"version": version}  # Specify the version here
            )
            if method == "GET":
                response = api_client.get(url, params)
            if method == "POST":
                response = api_client.post(url, params)

            assert response.status_code == status_code, description
            mock_get_exchange_rates.assert_called()
        except Exception as e:
            assert isinstance(e, NoReverseMatch), description
