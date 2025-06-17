"""
Dagster resources for the hass_datasette_etl project.
"""

import os
from dagster import ConfigurableResource
from dagster_snowflake import SnowflakeResource

# ---------------------------------------------------------------------
# Snowflake Resource
# ---------------------------------------------------------------------

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
