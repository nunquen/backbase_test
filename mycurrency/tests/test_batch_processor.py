import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date
from rates.service.batch_processor import batch_process


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
    with patch('rates.models.Currency.objects.get') as mock_get, \
         patch('rates.models.BatchProcess.objects.create') as mock_batch_process_create, \
         patch('rates.service.batch_processor.get_missing_rate_dates') as mock_get_missing_rate_dates, \
         patch('rates.models.BatchProcess.save') as mock_save:
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
