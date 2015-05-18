#!/bin/bash

set -e
set -x

# Export settings required to run psql non-interactively
export PGHOST=$(cat /etc/nyc-trees.d/env/NYC_TREES_DB_HOST)
export PGDATABASE=$(cat /etc/nyc-trees.d/env/NYC_TREES_DB_NAME)
export PGUSER=$(cat /etc/nyc-trees.d/env/NYC_TREES_DB_USER)
export PGPASSWORD=$(cat /etc/nyc-trees.d/env/NYC_TREES_DB_PASSWORD)

# Ensure that the PostGIS extension exists
psql -c "CREATE EXTENSION IF NOT EXISTS postgis;"

# Run migrations
envdir /etc/nyc-trees.d/env /opt/app/manage.py migrate

# Install the projection required for accurage geometry construction
envdir /etc/nyc-trees.d/env /opt/app/manage.py insert_state_plane_projection

# Load regions and assign to blocks
envdir /etc/nyc-trees.d/env /opt/app/manage.py loaddata /opt/app/apps/survey/fixtures/borough.json
envdir /etc/nyc-trees.d/env /opt/app/manage.py loaddata /opt/app/apps/survey/fixtures/neighborhoodtabulationarea.json
envdir /etc/nyc-trees.d/env /opt/app/manage.py assign_block_regions

# Load species data
envdir /etc/nyc-trees.d/env /opt/app/manage.py loaddata /opt/app/apps/survey/fixtures/species.json

# Setup soft launch flag if it does not already exist
if ! envdir /etc/nyc-trees.d/env /opt/app/manage.py flag -l | grep full_access; then
    envdir /etc/nyc-trees.d/env /opt/app/manage.py flag full_access --create
fi

# If a domain is not provided, default to treescount.nycgovparks.org
DJANGO_SITE_DOMAIN=${DJANGO_SITE_DOMAIN:-treescount.nycgovparks.org}

# Set django_sites name and domain
envdir /etc/nyc-trees.d/env /opt/app/manage.py set_django_site_domain \
    --django-site-name="${DJANGO_SITE_DOMAIN}" \
    --django-site-domain="${DJANGO_SITE_DOMAIN}"
