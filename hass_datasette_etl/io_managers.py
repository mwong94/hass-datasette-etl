import os
from clickhouse_io_manager import ClickHousePandasIOManager, ClickHouseConfig
from dagster_snowflake_pandas import SnowflakePandasIOManager

# ---------------------------------------------------------------------
# ClickHouse IO manager
# ---------------------------------------------------------------------
def get_clickhouse_config():
    """
    Create a ClickHouse config using environment variables.
    """
    return ClickHouseConfig(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_PORT", "8143")),
        user=os.getenv("CLICKHOUSE_USER", "default"),
        password=os.getenv("CLICKHOUSE_PASSWORD", ""),
        database=os.getenv("CLICKHOUSE_DB", "default"),
    )

clickhouse_io_manager = ClickHousePandasIOManager(
    config=get_clickhouse_config()
)

# ---------------------------------------------------------------------
# Snowflake IO manager
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