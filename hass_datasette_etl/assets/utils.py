import os
import json
import requests
import pandas as pd
from datetime import date, datetime, timedelta, UTC
from dagster import DailyPartitionsDefinition
import numpy as np
from typing import Any

# Define daily partitions starting from 2023-01-01
start_date = datetime(2023, 1, 1)
daily_partitions = DailyPartitionsDefinition(
    start_date=start_date,
    execution_timezone='America/Los_Angeles',
    hour_offset=0,
    minute_offset=15
)

# Base URL for the Datasette endpoint
DATASETTE_BASE_URL = os.environ.get("DATASETTE_BASE_URL", "http://192.168.1.138:8001")


def fetch_datasette_data(table_name, partition_date: str = '2025-01-01', context=None):
    """
    Fetch data from Datasette JSON endpoint for a specific table and date.
    Handles pagination to retrieve all rows.

    Args:
        table_name: Name of the table to fetch data from
        partition_date: Date to filter data for
        context: Optional AssetExecutionContext for logging

    Returns:
        DataFrame containing the fetched data
    """
    # Convert partition date to datetime
    date_obj = datetime.strptime(partition_date, "%Y-%m-%d")
    next_day = date_obj + timedelta(days=1)

    # Convert dates to unix timestamps
    start_timestamp = int(date_obj.timestamp())
    end_timestamp = int(next_day.timestamp())

    # Build URL for JSON API
    url = f"{DATASETTE_BASE_URL}/{table_name}.json"

    # Initial parameters
    params = {"_size": 1000, "_labels": "on"}  # Fetch 1000 rows per page

    # For statistics table, filter by date using created_ts (unix timestamp)
    if table_name == "statistics":
        params["created_ts__gte"] = start_timestamp
        params["created_ts__lt"] = end_timestamp

    # Get authentication token from environment if available
    auth_token = os.environ.get("DATASETTE_AUTH_TOKEN")
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    context.log.info(f"Using headers: {headers}")

    # Initialize an empty DataFrame to store all results
    all_data = pd.DataFrame()

    # Paginate through all results
    page_count = 0
    total_rows = 0

    if context:
        context.log.info(f"Starting pagination for {table_name} on {partition_date}")

    while True:
        page_count += 1
        if context:
            context.log.info(f"Fetching page {page_count} for {table_name}")
            context.log.info(f"\tURL: {url}")
            context.log.info(f"\tParams: {params}")

        # Make the request
        response = requests.get(url, params=params) #, headers=headers)
        response.raise_for_status()

        # Parse JSON response
        data = response.json()
        if context:
            context.log.debug(f"\tFetched json data")

        # If there are rows, add them to our DataFrame
        rows_in_page = 0
        if "rows" in data.keys() and data["rows"]:
            rows_in_page = len(data["rows"])
            total_rows += rows_in_page

            if context:
                context.log.info(f"Retrieved {rows_in_page} rows in page {page_count}, total rows so far: {total_rows}")

            if all_data.empty:
                all_data = pd.DataFrame(data["rows"], columns=data["columns"])
            else:
                new_data = pd.DataFrame(data["rows"], columns=data["columns"])
                all_data = pd.concat([all_data, new_data], ignore_index=True)

        # Check if there's a next page
        context.log.debug(f"\tNext URL: {data["next_url"]}")
        # context.log.info(data)
        if "next_url" in data.keys() and data["next_url"]:
            # Update params with the next page token
            url = data["next_url"]
            params = {}
            if context:
                context.log.debug(f"Moving to next page with url: {url}")
        else:
            # No more pages, exit the loop
            if context:
                context.log.debug(f"Pagination complete for {table_name}. Total pages: {page_count}, total rows: {total_rows}")
            break

    context.log.debug(f"{all_data.head().to_markdown()}")

    def _to_string(val: Any) -> str:
        if pd.isna(val):
            return ''

        if isinstance(val, (dict, list)):
            try:
                return json.dumps(val, ensure_ascii=False)
            except (TypeError, ValueError):
                # Fallback if object isn’t JSON-serialisable
                return str(val)

        # pandas.Timestamp or datetime
        if isinstance(val, (pd.Timestamp, datetime)):
            # Normalise to UTC
            if val.tzinfo is None:
                val = val.replace(tzinfo=UTC)
            else:
                val = val.astimezone(UTC)
            # Seconds → milliseconds, keep as int then str
            return str(int(val.timestamp() * 1000))

        # Pure date (exclude datetimes, which are already handled)
        if isinstance(val, date) and not isinstance(val, datetime):
            return val.isoformat()

        # Everything else
        return str(val)

    all_data = all_data.applymap(_to_string)
    # all_data = all_data.applymap(str)
    timestamp = datetime.timestamp(datetime.now(UTC))
    all_data["loaded_at"] = np.array([timestamp] * len(all_data), dtype=float)

    context.log.debug(timestamp)
    context.log.debug(all_data.loaded_at.head(10))

    return all_data

