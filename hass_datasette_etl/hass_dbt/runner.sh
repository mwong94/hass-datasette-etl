#!/bin/bash

set -a
source ../../.env
set +a

dbt run --profiles-dir ../profiles "$@"
