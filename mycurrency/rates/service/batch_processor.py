from asgiref.sync import sync_to_async
from datetime import date, timedelta
from uuid import uuid4

from ..models import Currency


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


async def batch_process(
    date_from: date,
    date_to: date
) -> uuid4:

    process_id = uuid4()

    # Get all currencies
    valid_currencies = await sync_to_async(
        lambda: set(Currency.objects.values_list("code", flat=True)),
        thread_sensitive=True
    )()

    # Prepare chunks
    max_years = 5
    date_ranges = split_date_range(
        date_from=date_from,
        date_to=date_to,
        years_per_chunk=max_years
    )
    
    # TODO: retrieve only those missing days in the database
     

    return process_id
