"""
State assets from Home Assistant Datasette
"""

from .utils import fetch_datasette_data
from datetime import datetime
from dagster import asset, AssetExecutionContext, DailyPartitionsDefinition, MetadataValue, ScheduleDefinition, define_asset_job, build_schedule_from_partitioned_job


# Define daily partitions starting from 2023-01-01
start_date = datetime(2025, 6, 7)
daily_partitions = DailyPartitionsDefinition(
    start_date=start_date,
    execution_timezone='America/Los_Angeles',
    hour_offset=0,
    minute_offset=15
)


@asset(
    name="events",
    group_name="hass",
    key_prefix="hass",
    partitions_def=daily_partitions,
    required_resource_keys={"clickhouse_io_manager"},
    io_manager_key="clickhouse_io_manager",
    metadata={"schema": "raw", "table": "events", "partition_expr": "time_fired_ts"},
)
def events(context: AssetExecutionContext):
    """
    Asset that extracts event data from Home Assistant Datasette endpoint
    and writes it to Clickhouse.
    """
    partition_date = context.partition_key
    context.log.info(f"Extracting events data for {partition_date}")

    # Fetch data from Datasette
    df = fetch_datasette_data(
        "events",
        partition_date=partition_date,
        partition_col="time_fired_ts",
        context=context
    )

    # Log metadata about the extraction
    context.add_output_metadata(
        metadata={
            "num_rows": len(df),
            "preview": MetadataValue.md(df.head().to_markdown() if not df.empty else "No data"),
            "partition_date": partition_date,
            "destination": "raw.events in Clickhouse",
        }
    )

    return df


@asset(
    name="event_data",
    group_name="hass",
    key_prefix="hass",
    required_resource_keys={"clickhouse_io_manager"},
    io_manager_key="clickhouse_io_manager",
    metadata={"schema": "raw", "table": "event_data"},
)
def event_data(context: AssetExecutionContext):
    """
    Asset that extracts event data from Home Assistant Datasette endpoint
    and writes it to Clickhouse.
    """

    # Fetch data from Datasette
    df = fetch_datasette_data(
        "event_data",
        context=context
    )

    # Log metadata about the extraction
    context.add_output_metadata(
        metadata={
            "num_rows": len(df),
            "preview": MetadataValue.md(df.head().to_markdown() if not df.empty else "No data"),
            "destination": "raw.event_data in Clickhouse",
        }
    )

    return df


@asset(
    name="event_types",
    group_name="hass",
    key_prefix="hass",
    required_resource_keys={"clickhouse_io_manager"},
    io_manager_key="clickhouse_io_manager",
    metadata={"schema": "raw", "table": "event_types"},
)
def event_types(context: AssetExecutionContext):
    """
    Asset that extracts event types from Home Assistant Datasette endpoint
    and writes it to Clickhouse.
    """

    # Fetch data from Datasette
    df = fetch_datasette_data(
        "event_types",
        context=context
    )

    # Log metadata about the extraction
    context.add_output_metadata(
        metadata={
            "num_rows": len(df),
            "preview": MetadataValue.md(df.head().to_markdown() if not df.empty else "No data"),
            "destination": "raw.event_types in Clickhouse",
        }
    )

    return df


##### events asset job and schedule
events_job = define_asset_job(
    name="events_job",
    selection=[events],
    description="Job that materializes the events asset"
)
events_schedule = build_schedule_from_partitioned_job(
    name="daily_events_schedule",
    job=events_job,
    description="Daily schedule for events asset"
)

##### event_data asset job and schedule
event_data_job = define_asset_job(
    name="event_data_job",
    selection=[event_data],
    description="Job that materializes the event_data asset"
)
event_data_schedule = ScheduleDefinition(
    name="daily_event_data_schedule",
    cron_schedule="20 0 * * *",
    job=event_data_job,
    execution_timezone="America/Los_Angeles",
    description="Daily schedule for event_data asset"
)

##### event_types asset job and schedule
event_types_job = define_asset_job(
    name="event_types_job",
    selection=[event_types],
    description="Job that materializes the event_types asset"
)
event_types_schedule = ScheduleDefinition(
    name="daily_event_types_schedule",
    cron_schedule="20 0 * * *",
    job=event_types_job,
    execution_timezone="America/Los_Angeles",
    description="Daily schedule for event_types asset"
)

# Group assets and schedules for export
events_assets = [events, event_data, event_types]
events_schedules = [events_schedule, event_data_schedule, event_types_schedule]
