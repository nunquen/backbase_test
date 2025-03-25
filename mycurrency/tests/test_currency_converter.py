import pytest
from django.urls import reverse
from unittest.mock import patch
from rest_framework import status
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


@pytest.mark.django_db
@pytest.mark.parametrize(
    "source_currency, exchanged_currency, amount, error_message, status_code, error_key, description",
    [
        (
            "USx",
            "GBP",
            1.2,
            "Invalid source_currency: USx",
            status.HTTP_400_BAD_REQUEST,
            "error",
            "> Testing invalid source_currency code",
        ),
        (
            "",
            "GBP",
            1.2,
            "This field may not be blank.",
            status.HTTP_400_BAD_REQUEST,
            "source_currency",
            "> Testing source_currency should not be blank",
        ),
        (
            "USDX",
            "GBP",
            1.2,
            "Ensure this field has no more than 3 characters.",
            status.HTTP_400_BAD_REQUEST,
            "source_currency",
            "> Testing source_currency should not has more than 3 characters.",
        ),
        (
            "USD",
            "GBx",
            1.2,
            "Invalid exchanged_currency: GBx",
            status.HTTP_400_BAD_REQUEST,
            "error",
            "> Testing invalid exchanged_currency code",
        ),
        (
            "USD",
            "",
            1.2,
            "This field may not be blank.",
            status.HTTP_400_BAD_REQUEST,
            "exchanged_currency",
            "> Testing exchanged_currency should not be blank",
        ),
        (
            "USD",
            "GBPX",
            1.2,
            "Ensure this field has no more than 3 characters.",
            status.HTTP_400_BAD_REQUEST,
            "exchanged_currency",
            "> Testing exchanged_currency should not has more than 3 characters.",
        ),
        (
            "USD",
            "GBP",
            "",
            "A valid number is required.",
            status.HTTP_400_BAD_REQUEST,
            "amount",
            "> Testing amount should be a number",
        ),
        (
            "USD",
            "GBP",
            "dummy value",
            "A valid number is required.",
            status.HTTP_400_BAD_REQUEST,
            "amount",
            "> Testing amount should be a number",
        ),
        (
            "USD",
            "GBP",
            1.01234123412431234,
            "Ensure that there are no more than 12 digits in total.",
            status.HTTP_400_BAD_REQUEST,
            "amount",
            "> Testing amount should be a number",
        ),
        (
            "USD",
            "GBP",
            0,
            "Ensure this value is greater than or equal to 0.01.",
            status.HTTP_400_BAD_REQUEST,
            "amount",
            "> Testing amount should be a positive number",
        ),
        (
            "USD",
            "GBP",
            0.999,
            "Ensure that there are no more than 2 decimal places.",
            status.HTTP_400_BAD_REQUEST,
            "amount",
            "> Testing amount should have 2 decimal places",
        ),
    ],
)
def test_currency_converter_input_parameters(
    clear_db,
    api_client,
    create_currencies,
    source_currency,
    exchanged_currency,
    amount,
    error_message,
    status_code,
    error_key,
    description,
):
    """Test with an invalid date format."""
    url = reverse(
        "currency-converter", kwargs={"version": "v1"}  # Specify the version here
    )
    response = api_client.get(
        url,
        {
            "source_currency": source_currency,
            "exchanged_currency": exchanged_currency,
            "amount": amount,
        },
    )
    response_data = response.json()
    assert (
        response.status_code == status_code
        and error_message in response_data[error_key]
    ), description


@pytest.mark.django_db
def test_currency_convertion_exception_handling(
    clear_db, api_client, create_currencies
):
    """Test unexpected exception handling."""
    with patch(
        "rates.views.get_exchange_convertion",
        side_effect=Exception("Something went wrong"),
    ) as mock_get_exchange_convertion:
        url = reverse(
            "currency-converter", kwargs={"version": "v1"}  # Specify the version here
        )
        response = api_client.get(
            url, {"source_currency": "USD", "exchanged_currency": "EUR", "amount": 1.0}
        )

        mock_get_exchange_convertion.assert_called()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Something went wrong" in response.json()["error"]
        # Assert that the patched function was called


@pytest.mark.django_db
def test_currency_convertion_success(clear_db, api_client, create_currencies):
    """Test success response."""
    with patch(
        "rates.views.get_exchange_convertion",
        return_value={
            "date": "2025-03-20",
            "from": "USD",
            "to": "EUR",
            "amount": 1.0,
            "value": 1.221674,
        },
    ) as mock_get_exchange_convertion:
        url = reverse(
            "currency-converter", kwargs={"version": "v1"}  # Specify the version here
        )
        response = api_client.get(
            url, {"source_currency": "USD", "exchanged_currency": "EUR", "amount": 1.0}
        )
        response_data = response.json()

        mock_get_exchange_convertion.assert_called()
        assert response.status_code == status.HTTP_200_OK
        assert 1.221674 == response_data["value"]
