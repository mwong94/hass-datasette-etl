#!/usr/bin/env sh
# Decide which Dagster command to run. Default: dev
set -eu

MODE="${DAGSTER_MODE:-dev}"

if [ "$MODE" = "prod" ]; then
  echo "Starting Dagster webserver (production mode)…"
  exec dagster webserver -h 0.0.0.0 -p 3000 -w workspace.yaml
else
  echo "Starting Dagster dev server…"
  exec /app/.venv/bin/dagster dev -h 0.0.0.0 -p 3000 -w workspace.yaml
fi
