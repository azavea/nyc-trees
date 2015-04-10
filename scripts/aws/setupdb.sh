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

for i in `seq 1 7`;
do
    envdir /etc/nyc-trees.d/env /opt/app/manage.py loaddata $DIR/../../src/nyc_trees/apps/survey/fixtures/blockface_$i.json
done

# Load species data
envdir /etc/nyc-trees.d/env /opt/app/manage.py loaddata $DIR/../../src/nyc_trees/apps/survey/fixtures/species.json

# Setup soft launch flag if it does not already exist
if ! envdir /etc/nyc-trees.d/env /opt/app/manage.py flag -l | grep full_access; then
    envdir /etc/nyc-trees.d/env /opt/app/manage.py flag full_access --create
fi

# Create training flatpages
envdir /etc/nyc-trees.d/env /opt/app/manage.py make_training_flatpages || true

# If a domain is not provided, default to treescount.nycgovparks.org
DJANGO_SITE_DOMAIN=${DJANGO_SITE_DOMAIN:-treescount.nycgovparks.org}

# Set django_sites name and domain
envdir /etc/nyc-trees.d/env /opt/app/manage.py set_django_site_domain \
    --django-site-name="${DJANGO_SITE_DOMAIN}" \
    --django-site-domain="${DJANGO_SITE_DOMAIN}"
