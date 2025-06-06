"""
Dagster resources for the hass_datasette_etl project.
"""

import os
from dagster import ConfigurableResource
from dagster_snowflake import SnowflakeResource
from dagster_snowflake_pandas import SnowflakePandasIOManager


class SnowflakeConfig(ConfigurableResource):
    """
    Configurable resource for Snowflake connection.
    """
    account: str
    user: str
    password: str
    database: str
    schema: str
    warehouse: str
    role: str


def get_snowflake_resource():
    """
    Create a Snowflake resource using environment variables.
    """
    return SnowflakeResource(
        account=os.environ.get("SNOWFLAKE_ACCOUNT"),
        user=os.environ.get("SNOWFLAKE_USER"),
        password=os.environ.get("SNOWFLAKE_PASSWORD"),
        database=os.environ.get("SNOWFLAKE_DATABASE"),
        schema=os.environ.get("SNOWFLAKE_SCHEMA", "raw"),
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE"),
        role=os.environ.get("SNOWFLAKE_ROLE"),
    )


# Define resources for export
snowflake_resource = get_snowflake_resource()
# ---------------------------------------------------------------------
# IO manager – uses same env-vars as the SnowflakeResource above
# ---------------------------------------------------------------------
snowflake_io_manager = SnowflakePandasIOManager(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA", "raw"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    role=os.getenv("SNOWFLAKE_ROLE"),
)