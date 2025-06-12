"""
Dagster project for extracting data from Home Assistant Datasette endpoint.
"""

from dagster import Definitions
from .assets import statistics_assets, statistics_schedules
from .resources import snowflake_resource
from .io_managers import clickhouse_io_manager, snowflake_io_manager

defs = Definitions(
    assets=statistics_assets,
    schedules=statistics_schedules,
    resources={
        "snowflake": snowflake_resource,
        "snowflake_io_manager": snowflake_io_manager,
        "clickhouse_io_manager": clickhouse_io_manager,
    },
)
