# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "clickhouse-connect",
#     "python-dotenv",
#     "typer",
# ]
# ///

#!/usr/bin/env python3
"""
SQLite to ClickHouse Migration Utility

This script migrates data from a SQLite database to a ClickHouse database.
It extracts all tables from the SQLite database and loads them into corresponding
tables in ClickHouse, using "create or replace table" to ensure tables are cleared
with each run.

Usage:
    python sqlite_to_clickhouse.py <sqlite_file> [OPTIONS]

Options:
    --table-filter TEXT                 Optional filter to process only specific tables (comma-separated)
    --clickhouse-host TEXT              ClickHouse host (defaults to CLICKHOUSE_HOST env var or 'localhost')
    --clickhouse-port INTEGER           ClickHouse port (defaults to CLICKHOUSE_PORT env var or 8143)
    --clickhouse-user TEXT              ClickHouse username (defaults to CLICKHOUSE_USER env var or 'default')
    --clickhouse-password TEXT          ClickHouse password (defaults to CLICKHOUSE_PASSWORD env var or '')
    --clickhouse-db TEXT                ClickHouse database (defaults to CLICKHOUSE_DB env var or 'default')
    --dotenv-path TEXT                  Path to the .env file (defaults to .env in the current directory)
    --help                              Show this message and exit.
"""

import os
import sqlite3
from typing import Dict, List, Optional, Any

import typer
import clickhouse_connect
from clickhouse_connect import driver
from dotenv import load_dotenv

app = typer.Typer(help="Migrate data from SQLite to ClickHouse")


def get_clickhouse_client(
    host: Optional[str] = None,
    port: Optional[int] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    database: Optional[str] = None,
    dotenv_path: Optional[str] = None
) -> driver.Client:
    """
    Create a ClickHouse client using provided parameters or environment variables.

    Args:
        host: ClickHouse host
        port: ClickHouse port
        username: ClickHouse username
        password: ClickHouse password
        database: ClickHouse database
        dotenv_path: Path to the .env file (defaults to .env in the current directory)
    """
    load_dotenv(dotenv_path=dotenv_path)

    return clickhouse_connect.get_client(
        host=host or os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=port or int(os.getenv("CLICKHOUSE_PORT", "8143")),
        username=username or os.getenv("CLICKHOUSE_USER", "default"),
        password=password or os.getenv("CLICKHOUSE_PASSWORD", ""),
        database=database or os.getenv("CLICKHOUSE_DB", "default"),
    )


def get_sqlite_tables(conn: sqlite3.Connection) -> List[str]:
    """
    Get a list of all tables in the SQLite database.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return tables


def get_sqlite_table_schema(conn: sqlite3.Connection, table_name: str) -> List[Dict[str, str]]:
    """
    Get the schema of a SQLite table.
    """
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [
        {
            "name": row[1],
            "type": row[2],
            "nullable": not row[3],  # notnull is 1 if the column is NOT NULL
        }
        for row in cursor.fetchall()
    ]
    cursor.close()
    return columns


def sqlite_type_to_clickhouse_type(sqlite_type: str) -> str:
    """
    Convert SQLite type to ClickHouse type.
    Using Nullable(String) for most types to prevent type casting errors.
    """
    sqlite_type = sqlite_type.upper()

    if "INT" in sqlite_type:
        return "Nullable(String)"
    elif "CHAR" in sqlite_type or "TEXT" in sqlite_type or "CLOB" in sqlite_type:
        return "Nullable(String)"
    elif "REAL" in sqlite_type or "FLOA" in sqlite_type or "DOUB" in sqlite_type:
        return "Nullable(String)"
    elif "BLOB" in sqlite_type:
        return "Nullable(String)"
    elif "DATE" in sqlite_type or "TIME" in sqlite_type:
        return "Nullable(String)"
    else:
        return "Nullable(String)"  # Default to Nullable(String) for unknown types


def create_clickhouse_table(
    client: driver.Client, 
    table_name: str, 
    columns: List[Dict[str, str]]
) -> None:
    """
    Create or replace a table in ClickHouse based on the SQLite schema.
    """
    # Generate column definitions
    column_defs = []
    for column in columns:
        ch_type = sqlite_type_to_clickhouse_type(column["type"])
        column_defs.append(f"`{column['name']}` {ch_type}")

    # Create the table
    create_table_sql = f"""
    CREATE OR REPLACE TABLE `{table_name}` (
        {', '.join(column_defs)}
    ) ENGINE = MergeTree() ORDER BY tuple()
    """

    client.command(create_table_sql)
    print(f"Created table {table_name} in ClickHouse")


def extract_sqlite_data(conn: sqlite3.Connection, table_name: str) -> List[Dict[str, Any]]:
    """
    Extract data from a SQLite table.
    """
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")

    # Get column names
    columns = [description[0] for description in cursor.description]

    # Fetch all rows and convert to list of dictionaries
    rows = cursor.fetchall()
    data = []
    for row in rows:
        data.append(dict(zip(columns, row)))

    cursor.close()
    return data


def load_data_to_clickhouse(
    client: driver.Client, 
    table_name: str, 
    data: List[Dict[str, Any]]
) -> None:
    """
    Load data into a ClickHouse table.
    """
    if not data:
        print(f"No data to load for table {table_name}")
        return

    # Get column names from the first row
    columns = list(data[0].keys())

    # Convert data to list of lists for clickhouse-connect
    # Ensure all values are properly converted to strings to avoid len() errors with integers
    rows = [[str(row.get(col)) if row.get(col) is not None else None for col in columns] for row in data]

    # Insert data
    client.insert(table_name, rows, column_names=columns)
    print(f"Loaded {len(rows)} rows into {table_name}")


@app.command()
def migrate(
    sqlite_file: str = typer.Argument(..., help="Path to the SQLite database file"),
    table_filter: Optional[str] = typer.Option(None, help="Optional filter to process only specific tables (comma-separated)"),
    clickhouse_host: Optional[str] = typer.Option(None, help="ClickHouse host (defaults to CLICKHOUSE_HOST env var or 'localhost')"),
    clickhouse_port: Optional[int] = typer.Option(None, help="ClickHouse port (defaults to CLICKHOUSE_PORT env var or 8143)"),
    clickhouse_user: Optional[str] = typer.Option(None, help="ClickHouse username (defaults to CLICKHOUSE_USER env var or 'default')"),
    clickhouse_password: Optional[str] = typer.Option(None, help="ClickHouse password (defaults to CLICKHOUSE_PASSWORD env var or '')"),
    clickhouse_db: Optional[str] = typer.Option(None, help="ClickHouse database (defaults to CLICKHOUSE_DB env var or 'default')"),
    dotenv_path: Optional[str] = typer.Option(None, help="Path to the .env file (defaults to .env in the current directory)")
) -> None:
    """
    Migrate data from SQLite to ClickHouse.
    """
    # Validate SQLite file exists
    if not os.path.exists(sqlite_file):
        typer.echo(f"Error: SQLite file {sqlite_file} does not exist")
        raise typer.Exit(code=1)

    # Parse table filter if provided
    tables_to_process = None
    if table_filter:
        tables_to_process = [t.strip() for t in table_filter.split(",")]

    # Connect to SQLite
    try:
        sqlite_conn = sqlite3.connect(sqlite_file)
        typer.echo(f"Connected to SQLite database: {sqlite_file}")
    except sqlite3.Error as e:
        typer.echo(f"Error connecting to SQLite database: {e}")
        raise typer.Exit(code=1)

    # Connect to ClickHouse
    try:
        clickhouse_client = get_clickhouse_client(
            host=clickhouse_host,
            port=clickhouse_port,
            username=clickhouse_user,
            password=clickhouse_password,
            database=clickhouse_db,
            dotenv_path=dotenv_path
        )
        db_name = clickhouse_db or os.getenv("CLICKHOUSE_DB", "default")
        typer.echo(f"Connected to ClickHouse database: {db_name}")
    except Exception as e:
        typer.echo(f"Error connecting to ClickHouse database: {e}")
        sqlite_conn.close()
        raise typer.Exit(code=1)

    try:
        # Get all tables from SQLite
        all_tables = get_sqlite_tables(sqlite_conn)

        # Filter tables if needed
        tables = all_tables
        if tables_to_process:
            tables = [t for t in all_tables if t in tables_to_process]
            missing_tables = [t for t in tables_to_process if t not in all_tables]
            if missing_tables:
                typer.echo(f"Warning: The following requested tables were not found: {', '.join(missing_tables)}")

        typer.echo(f"Found {len(tables)} tables to process")

        # Process each table
        for table_name in tables:
            typer.echo(f"\nProcessing table: {table_name}")

            # Get table schema
            columns = get_sqlite_table_schema(sqlite_conn, table_name)

            # Create table in ClickHouse
            create_clickhouse_table(clickhouse_client, table_name, columns)

            # Extract data from SQLite
            data = extract_sqlite_data(sqlite_conn, table_name)
            typer.echo(f"Extracted {len(data)} rows from {table_name}")

            # Load data to ClickHouse
            load_data_to_clickhouse(clickhouse_client, table_name, data)

        typer.echo("\nMigration completed successfully")

    except Exception as e:
        typer.echo(f"Error during migration: {e}")
        raise typer.Exit(code=1)

    finally:
        # Clean up connections
        sqlite_conn.close()
        clickhouse_client.close()


if __name__ == "__main__":
    app()
