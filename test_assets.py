"""
Test script for Dagster assets.

This script materializes the Dagster assets for a specific date to test the implementation.
"""

import os
import sys
from datetime import datetime

from dagster import materialize, DailyPartitionsDefinition

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath("."))

# Import the assets and resources
from hass_datasette_etl.assets import statistics, statistics_meta
from hass_datasette_etl.resources import snowflake_resource

def test_assets():
    """Test materializing the assets for a specific date."""
    # Use a fixed date within the valid partition range
    test_date = "2023-06-01"

    print(f"Testing assets for date: {test_date}")

    # Materialize the statistics asset
    print("\nMaterializing statistics asset...")
    result = materialize(
        [statistics],
        partition_key=test_date,
        resources={"snowflake": snowflake_resource},
    )
    print(f"Statistics asset materialization {'succeeded' if result.success else 'failed'}")

    # Materialize the statistics_meta asset (no partition needed)
    print("\nMaterializing statistics_meta asset...")
    result = materialize(
        [statistics_meta],
        resources={"snowflake": snowflake_resource},
    )
    print(f"Statistics_meta asset materialization {'succeeded' if result.success else 'failed'}")

if __name__ == "__main__":
    test_assets()
