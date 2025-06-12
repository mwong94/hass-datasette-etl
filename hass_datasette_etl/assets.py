"""
Dagster assets for extracting data from Home Assistant Datasette endpoint.
"""

import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dagster import asset, AssetExecutionContext, DailyPartitionsDefinition, MetadataValue, ScheduleDefinition, define_asset_job, build_schedule_from_partitioned_job
from dagster_snowflake import SnowflakeResource
from snowflake.connector.pandas_tools import write_pandas


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

    all_data["loaded_at"] = datetime.now()

    return all_data


@asset(
    name="statistics",
    partitions_def=daily_partitions,
    required_resource_keys={"snowflake_io_manager"},
    io_manager_key="snowflake_io_manager",
    metadata={"schema": "raw", "table": "statistics", "partition_expr": "created_ts"},
)
def statistics(context: AssetExecutionContext):
    """
    Asset that extracts statistics data from Home Assistant Datasette endpoint
    and writes it to Snowflake.
    """
    partition_date = context.partition_key
    context.log.info(f"Extracting statistics data for {partition_date}")

    # Fetch data from Datasette
    df = fetch_datasette_data("statistics", partition_date, context)

    # Log metadata about the extraction
    context.add_output_metadata(
        metadata={
            "num_rows": len(df),
            "preview": MetadataValue.md(df.head().to_markdown() if not df.empty else "No data"),
            "partition_date": partition_date,
            "destination": "hass.raw.statistics in Snowflake",
        }
    )

    return df


@asset(
    name="statistics_meta",
    metadata={"schema": "raw", "table": "statistics_meta"},
)
def statistics_meta(context: AssetExecutionContext, snowflake: SnowflakeResource):
    """
    Asset that extracts statistics metadata from Home Assistant Datasette endpoint
    and appends it to Snowflake table without truncating previous data.
    """
    context.log.info(f"Extracting statistics metadata")

    # Fetch all metadata data from Datasette
    df = fetch_datasette_data("statistics_meta", context=context)

    # Log metadata about the extraction
    context.add_output_metadata(
        metadata={
            "num_rows": len(df),
            "preview": MetadataValue.md(df.head().to_markdown() if not df.empty else "No data"),
            "destination": "hass.raw.statistics_meta in Snowflake",
            "extraction_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )

    # Append data to Snowflake table
    if not df.empty:
        # Connect to Snowflake and write data
        with snowflake.get_connection() as conn:
            context.log.info(f"Appending {len(df)} rows to statistics_meta table")

            # Use write_pandas from snowflake.connector.pandas_tools
            df.columns = [col.upper() for col in df.columns]
            success, num_chunks, num_rows, _ = write_pandas(
                conn=conn,
                df=df,
                table_name="STATISTICS_META",
                database=os.environ.get('SNOWFLAKE_DATABASE').upper(),
                schema="RAW",
                auto_create_table=False
            )

            if success:
                context.log.info(f"Successfully appended {num_rows} rows in {num_chunks} chunks")
            else:
                raise Exception("Failed to write data to Snowflake")

    return df

##### statistics asset job and schedule
statistics_job = define_asset_job(
    name="statistics_job",
    selection=[statistics],
    description="Job that materializes the statistics asset"
)
statistics_schedule = build_schedule_from_partitioned_job(
    name="daily_statistics_schedule",
    job=statistics_job,
    description="Daily schedule for statistics asset"
)

##### statistics_meta asset job and schedule
statistics_meta_job = define_asset_job(
    name="statistics_meta_job",
    selection=[statistics],
    description="Job that materializes the statistics asset"
)
statistics_meta_schedule = ScheduleDefinition(
    name="weekly_statistics_meta_schedule",
    cron_schedule="20 0 * * 0",  # 00:20 on Sunday morning
    job=statistics_meta_job,
    execution_timezone="America/Los_Angeles",
    description="Weekly schedule for statistics_meta asset"
)

# Group assets and schedules for export
statistics_assets = [statistics, statistics_meta]
statistics_schedules = [statistics_schedule, statistics_meta_schedule]
