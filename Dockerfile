# Use Python 3.12 as the base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install git and clean up apt cache
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin:$PATH"

# Copy project files
COPY pyproject.toml uv.lock ./
COPY workspace.yaml .

# Install dependencies
# RUN pip install --no-cache-dir -e .
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN uv sync --locked

# Set environment variables
ENV PYTHONPATH=/app
ENV DAGSTER_HOME=/app/dagster_home
ENV DBT_PROFILES_DIR=/app/hass_datasette_etl/profiles

# Create dagster home directory
RUN mkdir -p $DAGSTER_HOME

# Copy Dagster configuration
COPY dagster.yaml $DAGSTER_HOME/

# Entrypoint using shell script to manage dev vs prod modes
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 3000
ENTRYPOINT ["docker-entrypoint.sh"]
