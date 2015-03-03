#!/bin/bash

set -e
set -x

DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)

# Export settings required to run psql non-interactively
export PGHOST=$(cat /etc/nyc-trees.d/env/NYC_TREES_DB_HOST)
export PGDATABASE=$(cat /etc/nyc-trees.d/env/NYC_TREES_DB_NAME)
export PGUSER=$(cat /etc/nyc-trees.d/env/NYC_TREES_DB_USER)
export PGPASSWORD=$(cat /etc/nyc-trees.d/env/NYC_TREES_DB_PASSWORD)

# Ensure that the PostGIS extension exists
psql -c "CREATE EXTENSION IF NOT EXISTS postgis;"

# Run migrations
envdir /etc/nyc-trees.d/env /opt/app/manage.py migrate
# Load block face data
envdir /etc/nyc-trees.d/env /opt/app/manage.py loaddata $DIR/../src/nyc_trees/apps/survey/fixtures/blockface.json

# Setup soft launch flag if it does not already exist
if ! envdir /etc/nyc-trees.d/env /opt/app/manage.py flag -l | grep full_access; then
    envdir /etc/nyc-trees.d/env /opt/app/manage.py flag full_access --create
fi

# Create training flatpages
envdir /etc/nyc-trees.d/env /opt/app/manage.py make_training_flatpages || true
