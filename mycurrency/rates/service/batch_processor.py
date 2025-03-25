import asyncio
import logging
from asgiref.sync import sync_to_async
from datetime import date, timedelta
from django.conf import settings
from django.utils import timezone
from typing import List
from uuid import uuid4

from ..adapters.adapter_factory import (
    get_exchange_rate_data
)
from ..models import BatchProcess, Currency, CurrencyExchangeRate
from .common import get_missing_rate_dates


logger = logging.getLogger(__name__)


def split_date_range(
    date_from: date,
    date_to: date,
    years_per_chunk: int
) -> list[dict[str, date]]:
    # Initialize the list to hold the date ranges
    date_ranges = []

    # Calculate the time delta for the specified number of years
    delta = timedelta(days=years_per_chunk * 365)

    # Iterate over the date range, creating chunks
    while date_from < date_to:
        chunk_end_date = min(date_from + delta, date_to)
        date_ranges.append({
            "date_from": date_from,
            "date_to": chunk_end_date
        })
        date_from = chunk_end_date + timedelta(days=1)

    return date_ranges


# Synchronous wrapper function
def sync_get_missing_rate_dates(
    source_currency: str,
    date_from: date,
    date_to: date
) -> List:
    missing_rates_dates = get_missing_rate_dates(source_currency, date_from, date_to)
    return missing_rates_dates


def fetch_remote_data(
    source_currency: str,
    exchanged_currencies: str,
    date_range: List,
    process_id: uuid4
):
    logger.info("Fetching remote data for source_currency {}".format(
        source_currency
    ))
    try:
        data, provider = get_exchange_rate_data(
            source_currency=source_currency,
            exchanged_currency=exchanged_currencies,
            date_from=date_range[0],
            date_to=date_range[-1]
        )
        logger.info("fetch_remote_data using {}: data is {}".format(provider, data))
        if not data:
            return

        # Saving data in data base
        for date_rate, currency_data in data.items():
            for currency, rate in currency_data.items():
                if rate is None:
                    continue

                source_currency_obj = Currency.objects.get(code=source_currency)
                exchanged_obj = Currency.objects.get(code=currency)

                CurrencyExchangeRate.objects.get_or_create(
                    source_currency=source_currency_obj,
                    exchanged_currency=exchanged_obj,
                    valuation_date=date_rate,
                    defaults={"rate_value": rate},
                )
        # Recovering batch process from database and updating counter and status
        batch_process_instance = BatchProcess.objects.get(
            process_id=process_id
        )
        batch_process_instance.processes_counter += 1
        if batch_process_instance.processes_counter == batch_process_instance.processes:
            batch_process_instance.status = BatchProcess.Status.DONE
            batch_process_instance.ending_time = timezone.now()
            batch_process_instance.save(
                update_fields=['processes_counter', 'status', 'ending_time']
            )
        else:
            batch_process_instance.save(update_fields=['processes_counter'])
    except Exception as e:
        raise e


async def batch_process(
    source_currency: str,
    valid_currencies: set,
    date_from: date,
    date_to: date
) -> uuid4:
    batch_process_instance = await sync_to_async(
        lambda: BatchProcess.objects.create(
            source_currency=Currency.objects.get(code=source_currency)
        ),
        thread_sensitive=True
    )()

    # Removing source currency and getting the exchanged currencies
    exchanged_currencies = ",".join(valid_currencies - {source_currency})

    # Prepare chunks
    max_years = getattr(settings, 'BATCH_PROCESS_MAX_YEARS_TO_RETRIEVE', 5)
    date_ranges = split_date_range(
        date_from=date_from,
        date_to=date_to,
        years_per_chunk=max_years
    )

    # Retrieve only those missing days in the database
    async_get_missing_rate_dates = sync_to_async(
        sync_get_missing_rate_dates,
        thread_sensitive=False
    )
    logger.info(
        "batch_process: processing {} date ranges".format(len(date_ranges))
    )
    # Calculating batch calls to be done
    batch_calls = 0
    for date_range in date_ranges:
        missing_rate_dates = await async_get_missing_rate_dates(
            source_currency=source_currency,
            date_from=date_range["date_from"],
            date_to=date_range["date_to"]
        )
        # batch calls are only for missing dates in the database
        if missing_rate_dates:
            batch_calls += len(missing_rate_dates)

    if batch_calls == 0:
        # FINALIZING CURRENT BATCH PROCESS
        batch_process_instance.status = BatchProcess.Status.DONE
        await sync_to_async(
            batch_process_instance.save,
            thread_sensitive=True
        )(update_fields=['status'])
        return batch_process_instance.process_id

    # Updating the BatchProcess with the processes value
    batch_process_instance.processes = batch_calls
    await sync_to_async(batch_process_instance.save)(update_fields=['processes'])

    # Concurrency: processing batch async tasks
    sleep_time = getattr(settings, 'BATCH_PROCESS_SLEEP_TIME', 0.2)
    for date_range in date_ranges:
        # Fetching form remote api only those missing dates in the database
        missing_rate_dates = await async_get_missing_rate_dates(
            source_currency=source_currency,
            date_from=date_range["date_from"],
            date_to=date_range["date_to"]
        )
        logger.info(
            "batch_process: >> working on date range {} - processing {} sub date ranges".format(  # noqa: E501
                date_ranges,
                len(missing_rate_dates)
            )
        )
        # Iterate over each subset of missing dates
        for subset in missing_rate_dates:
            try:
                # Schedule the fetch_remote_data call as a task
                async with asyncio.TaskGroup() as task_group:
                    task_group.create_task(asyncio.to_thread(
                        fetch_remote_data,
                        source_currency,
                        exchanged_currencies,
                        subset,
                        batch_process_instance.process_id
                    ))
                # Wait for 0.2 secs before the next task to avoid remote api error
                await asyncio.sleep(sleep_time)
            except* Exception as eg:
                # Handle multiple exceptions raised within the TaskGroup
                logging.error(f"batch_process - An error occurred: {eg.exceptions[0]}")
                # Optionally, re-raise the exception group if further action is needed
                raise eg.exceptions[0]

    return batch_process_instance.process_id
