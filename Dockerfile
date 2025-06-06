# Use Python 3.12 as the base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY workspace.yaml .
#COPY hass_datasette_etl ./hass_datasette_etl

# Install dependencies
RUN pip install --no-cache-dir -e .

# Set environment variables
ENV PYTHONPATH=/app
ENV DAGSTER_HOME=/app/dagster_home

# Create dagster home directory
RUN mkdir -p $DAGSTER_HOME

# Copy Dagster configuration
COPY dagster.yaml $DAGSTER_HOME/

# Expose Dagster webserver port
EXPOSE 3000

# Command to run Dagster webserver
CMD ["dagster", "dev", "-h", "0.0.0.0", "-p", "3000", "-w", "workspace.yaml"]