"""
Dagster project for extracting data from Home Assistant Datasette endpoint.
"""

from dagster import Definitions
from .assets import statistics_assets, statistics_schedules, events_assets, events_schedules
from .resources import snowflake_resource
from .io_managers import clickhouse_io_manager, snowflake_io_manager
from .hass_dbt.definitions import dbt_defs

hass_defs = Definitions(
    assets=statistics_assets+events_assets,
    schedules=statistics_schedules+events_schedules,
    resources={
        "snowflake": snowflake_resource,
        "snowflake_io_manager": snowflake_io_manager,
        "clickhouse_io_manager": clickhouse_io_manager,
    },
)

defs = Definitions.merge(hass_defs, dbt_defs)
