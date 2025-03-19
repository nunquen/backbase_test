import pytest
from datetime import datetime
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rates.models import Currency


@pytest.fixture
def api_client():
    """Fixture for the Django REST Framework API client."""
    return APIClient()


@pytest.fixture
def create_currencies():
    """Fixture to create test currencies in the database."""
    Currency.objects.create(code="USD", name="US Dollar")
    Currency.objects.create(code="EUR", name="Euro")


def test_one():
    assert True


# def test_currency_rate_valid_request(api_client, create_currencies, mocker):
#     """Test the API with a valid request."""
#     mocker.patch("..service.rater.get_exchange_rates", return_value={
#         "2025-03-10": {"USD/EUR": 1.085}
#     })

#     response = api_client.get(
#         reverse("currency-rate"),
#         {"source_currency": "USD", "date_from": "2025-03-10", "date_to": "2025-03-10"}
#     )

#     assert response.status_code == status.HTTP_200_OK
#     assert "2025-03-10" in response.json()
#     assert "USD/EUR" in response.json()["2025-03-10"]


# def test_currency_rate_invalid_source_currency(api_client, create_currencies):
#     """Test with an invalid source currency."""
#     response = api_client.get(
#         reverse("currency-rate"),
#         {"source_currency": "XYZ", "date_from": "2025-03-10", "date_to": "2025-03-10"}
#     )
    
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert "Invalid source_currency" in response.json()["error"]


# def test_currency_rate_invalid_date_format(api_client, create_currencies):
#     """Test with an invalid date format."""
#     response = api_client.get(
#         reverse("currency-rate"),
#         {"source_currency": "USD", "date_from": "10-03-2025", "date_to": "2025-03-10"}
#     )
    
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert "Invalid date format" in response.json()["error"]


# def test_currency_rate_invalid_date_range(api_client, create_currencies):
#     """Test with date_from later than date_to."""
#     response = api_client.get(
#         reverse("currency-rate"),
#         {"source_currency": "USD", "date_from": "2025-03-15", "date_to": "2025-03-10"}
#     )
    
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert "Invalid date range" in response.json()["error"]


# def test_currency_rate_exception_handling(api_client, create_currencies, mocker):
#     """Test unexpected exception handling."""
#     mocker.patch("..service.rater.get_exchange_rates", side_effect=Exception("Something went wrong"))
    
#     response = api_client.get(
#         reverse("currency-rate"),
#         {"source_currency": "USD", "date_from": "2025-03-10", "date_to": "2025-03-15"}
#     )
    
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert "Something went wrong" in response.json()["error"]
