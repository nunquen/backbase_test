import pytest
from asgiref.sync import sync_to_async
from datetime import date
from unittest.mock import MagicMock, patch
from rates.service.batch_processor import batch_process, fetch_remote_data

from rates.models import BatchProcess, Currency


@pytest.fixture
def clear_db():
    """Clears the database before each test to avoid UNIQUE constraint errors."""
    BatchProcess.objects.all().delete()
    Currency.objects.all().delete()


@pytest.fixture
def create_currencies():
    """Fixture to create test currencies in the database."""
    Currency.objects.get_or_create(code="USD", name="US Dollar", symbol="$")
    Currency.objects.get_or_create(code="EUR", name="Euro", symbol="€")


@pytest.mark.asyncio
async def test_batch_process_no_missing_dates(clear_db, create_currencies):
    with patch(
        'rates.service.batch_processor.get_missing_rate_dates'
    ) as mock_get_missing_rate_dates:
        mock_get_missing_rate_dates.return_value = []
        process_id = await batch_process(
            source_currency='USD',
            valid_currencies={'USD', 'EUR'},
            date_from=date(2025, 3, 1),
            date_to=date(2025, 3, 31)
        )

        process = await sync_to_async(
            BatchProcess.objects.get,
            thread_sensitive=False
        )(process_id=process_id)
        assert process.status == BatchProcess.Status.DONE


@pytest.mark.asyncio
async def test_batch_process():
    mock_currency = MagicMock()
    mock_currency.code = 'USD'

    # Mock the BatchProcess model's 'create' method
    # mock_batch_process = MagicMock()
    mock_batch_process_instance = MagicMock()
    mock_batch_process_instance.process_id = 123
    # mock_batch_process.return_value = mock_batch_process_instance

    # Patch the 'get' and 'create' methods
    with patch(
        'rates.models.Currency.objects.get'
    ) as mock_get, patch(
        'rates.models.BatchProcess.objects.create'
    ) as mock_batch_process_create, patch(
        'rates.service.batch_processor.get_missing_rate_dates'
    ) as mock_get_missing_rate_dates, patch(
        'rates.models.BatchProcess.save'
    ) as mock_save:
        mock_get.return_value = mock_currency
        mock_batch_process_create.return_value = mock_batch_process_instance
        mock_get_missing_rate_dates.return_value = []
        mock_save.return_value = None
        # Call the function
        process_id = await batch_process(
            source_currency='USD',
            valid_currencies={'USD', 'EUR'},
            date_from=date(2025, 3, 1),
            date_to=date(2025, 3, 31)
        )

        # Assertions
        mock_get.assert_called_once_with(code='USD')
        mock_batch_process_create.assert_called_once()
        assert process_id == mock_batch_process_instance.process_id


def test_fetch_remote_data():
    with patch(
        'rates.service.batch_processor.get_exchange_rate_data'
    ) as mock_get_exchange_rate_data:
        mock_get_exchange_rate_data.return_value = ({'2024-11-29': {'EUR': 0.94531809}}, 'mockprovider')

        batch_process = BatchProcess.objects.create(
            source_currency=Currency.objects.get(code="USD"),
            processes=1
        )

        fetch_remote_data(
            source_currency="USD",
            exchanged_currencies="EUR",
            date_range=[date(2025, 3, 1)],
            process_id=batch_process.process_id
        )

        batch_process_updated = BatchProcess.objects.get(
            process_id=batch_process.process_id
        )
        assert batch_process_updated.processes_counter == 1
        assert batch_process_updated.status == BatchProcess.Status.DONE
