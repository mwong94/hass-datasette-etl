"""
Statistics assets from Home Assistant Datasette
"""

from .utils import daily_partitions, fetch_datasette_data

from datetime import datetime
from dagster import asset, AssetExecutionContext, MetadataValue, ScheduleDefinition, define_asset_job, build_schedule_from_partitioned_job


@asset(
    name="statistics",
    group_name="hass",
    key_prefix="hass",
    partitions_def=daily_partitions,
    required_resource_keys={"clickhouse_io_manager"},
    io_manager_key="clickhouse_io_manager",
    metadata={"schema": "raw", "table": "statistics", "partition_expr": "created_ts"},
)
def statistics(context: AssetExecutionContext):
    """
    Asset that extracts statistics data from Home Assistant Datasette endpoint
    and writes it to Clickhouse.
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
            "destination": "raw.statistics in Clickhouse",
        }
    )

    return df


@asset(
    name="statistics_meta",
    group_name="hass",
    key_prefix="hass",
    metadata={"schema": "raw", "table": "statistics_meta"},
    io_manager_key="clickhouse_io_manager",
)
def statistics_meta(context: AssetExecutionContext):
    """
    Asset that extracts statistics metadata from Home Assistant Datasette endpoint
    and appends it to Clickhouse table without truncating previous data.
    """
    context.log.info(f"Extracting statistics metadata")

    # Fetch all metadata data from Datasette
    df = fetch_datasette_data("statistics_meta", context=context)

    # Log metadata about the extraction
    context.add_output_metadata(
        metadata={
            "num_rows": len(df),
            "preview": MetadataValue.md(df.head().to_markdown() if not df.empty else "No data"),
            "destination": "raw.statistics_meta in Clickhouse. Truncating previous data if any.",
            "extraction_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )

    # Append data to Snowflake table
    # if not df.empty:
    #     # Connect to Snowflake and write data
    #     with snowflake.get_connection() as conn:
    #         context.log.info(f"Appending {len(df)} rows to statistics_meta table")
    #
    #         # Use write_pandas from snowflake.connector.pandas_tools
    #         df.columns = [col.upper() for col in df.columns]
    #         success, num_chunks, num_rows, _ = write_pandas(
    #             conn=conn,
    #             df=df,
    #             table_name="STATISTICS_META",
    #             database=os.environ.get('SNOWFLAKE_DATABASE').upper(),
    #             schema="RAW",
    #             auto_create_table=False
    #         )
    #
    #         if success:
    #             context.log.info(f"Successfully appended {num_rows} rows in {num_chunks} chunks")
    #         else:
    #             raise Exception("Failed to write data to Snowflake")

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
