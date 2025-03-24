import pytest
from datetime import datetime
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest import mock
from unittest.mock import patch

from rates.models import Currency


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
    # Currency.objects.get_or_create(code="GBP", name="Pound Sterling", symbol="£")
    # Currency.objects.get_or_create(code="CHF", name="Swiss Franc", symbol="CHF")


@pytest.mark.django_db
def test_currency_rate_invalid_source_currency(api_client, create_currencies):
    """Test with an invalid source currency."""
    response = api_client.get(
        reverse("currency-rates"),
        {"source_currency": "XYZ", "date_from": "2025-03-10", "date_to": "2025-03-10"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid source_currency" in response.json()["error"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "source_currency, date_from, date_to, error_message, status_code, description", [
        (
            "USD",
            "10-03-2025",
            "2025-03-10",
            "Invalid date_from format",
            status.HTTP_400_BAD_REQUEST,
            "> Validating bad date_from format"
        ),
        (
            "USD",
            "2025-03-10",
            "2025-13-10",
            "Invalid date_to format",
            status.HTTP_400_BAD_REQUEST,
            "> Validating bad date_to format"
        ),
        (
            "USD",
            "2025-03-10",
            "2025-03-01",
            "Invalid date range",
            status.HTTP_400_BAD_REQUEST,
            "> Validating bad date range"
        )
    ]
)
def test_currency_rate_invalid_date_format(
    api_client,
    create_currencies,
    source_currency,
    date_from,
    date_to,
    error_message,
    status_code,
    description
):
    """Test with an invalid date format."""
    response = api_client.get(
        reverse("currency-rates"),
        {
            "source_currency": source_currency,
            "date_from": date_from,
            "date_to": date_to
        }
    )

    assert response.status_code == status_code and error_message in response.json()["error"], description


@pytest.mark.django_db
def test_currency_rate_exception_handling(api_client, create_currencies):
    """Test unexpected exception handling."""
    with patch(
        "rates.views.get_exchange_rates",
        side_effect=Exception("Something went wrong")
    ) as mock_get_exchange_rates:

        response = api_client.get(
            reverse("currency-rates"),
            {"source_currency": "USD", "date_from": "2025-03-10", "date_to": "2025-03-15"}
        )

        mock_get_exchange_rates.assert_called()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Something went wrong" in response.json()["error"]
        # Assert that the patched function was called


@pytest.mark.django_db
def test_currency_rate_valid_request(api_client, create_currencies):
    """Test the API with a valid request."""
    with patch(
        "rates.views.get_exchange_rates",
        return_value={
            "2025-03-10": {"USD/EUR": 1.085}
        }
    ) as mock_get_exchange_rates:

        response = api_client.get(
            reverse("currency-rates"),
            {"source_currency": "USD", "date_from": "2025-03-10", "date_to": "2025-03-15"}
        )

        mock_get_exchange_rates.assert_called()
        assert response.status_code == status.HTTP_200_OK
        assert "2025-03-10" in response.json()
        assert "USD/EUR" in response.json()["2025-03-10"]
