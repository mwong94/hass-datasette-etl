# Home Assistant Datasette ETL

A Dagster project to extract data from a Home Assistant Datasette endpoint. This project extracts data from the `statistics` and `statistics_meta` tables on an hourly basis and writes the data to Snowflake.

## Features

- Extracts data from Home Assistant Datasette endpoint
- Writes data to Snowflake tables
- Uses Dagster's asset feature with daily partitioning for easy backfills
- Dockerized application with Docker Compose
- Environment variable configuration

## Requirements

- Docker and Docker Compose
- Home Assistant instance with Datasette endpoint
- Snowflake account with appropriate permissions

## Setup

1. Clone this repository
2. Create a `.env` file based on the `.env.example` template:

```bash
cp .env.example .env
```

3. Edit the `.env` file to configure your Datasette endpoint, Snowflake credentials, and other settings:

```
# Datasette configuration
DATASETTE_BASE_URL=http://192.168.1.138:8001
DATASETTE_AUTH_TOKEN=your_auth_token_if_needed

# Dagster configuration
DAGSTER_HOME=/app/dagster_home

# Snowflake configuration
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=raw
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_ROLE=your_role

# Logging level
LOG_LEVEL=INFO
```

Note: Make sure to set up the Snowflake tables `hass.raw.statistics` and `hass.raw.statistics_meta` before running the application.

## Running the Application

Start the application using Docker Compose:

```bash
docker-compose up -d
```

This will start:
- Dagster webserver on port 3000
- Dagster daemon for running schedules and sensors

Access the Dagster UI at http://localhost:3000

## Using the Application

### Assets

The application defines two assets:

1. `statistics` - Extracts data from the statistics table and writes it to `hass.raw.statistics` in Snowflake
2. `statistics_meta` - Extracts data from the statistics_meta table and writes it to `hass.raw.statistics_meta` in Snowflake

Both assets are partitioned daily, allowing you to:
- Materialize data for specific dates
- Perform backfills for date ranges
- Schedule regular materializations
- Append data to existing Snowflake tables

### Materializing Assets

You can materialize assets for specific dates through the Dagster UI:

1. Navigate to the Assets page
2. Select the assets you want to materialize
3. Click "Materialize selected"
4. Choose the partition(s) you want to materialize
5. Click "Materialize"

### Scheduling

You can set up schedules to materialize assets on a regular basis:

1. Navigate to the Schedules page
2. Create a new schedule for the assets
3. Configure the schedule timing
4. Activate the schedule

## Project Structure

- `hass_datasette_etl/` - Main package directory
  - `__init__.py` - Package initialization and Dagster definitions
  - `assets.py` - Dagster assets for extracting data and writing to Snowflake
  - `resources.py` - Dagster resources including Snowflake connection
- `Dockerfile` - Docker configuration
- `docker-compose.yml` - Docker Compose configuration
- `dagster.yaml` - Dagster configuration
- `.env.example` - Example environment variables
- `test_assets.py` - Script for testing asset materialization

## Development

To develop locally:

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install the package in development mode:
```bash
pip install -e .
```

3. Run the Dagster UI:
```bash
dagster dev
```
