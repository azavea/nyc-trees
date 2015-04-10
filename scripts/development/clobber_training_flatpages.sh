#!/bin/bash

# Reload the training flatpages in just one command

set -e

ARGS=$*

vagrant ssh app -c '
export PGHOST=$(cat /etc/nyc-trees.d/env/NYC_TREES_DB_HOST) &&
export PGDATABASE=$(cat /etc/nyc-trees.d/env/NYC_TREES_DB_NAME) &&
export PGUSER=$(cat /etc/nyc-trees.d/env/NYC_TREES_DB_USER) &&
export PGPASSWORD=$(cat /etc/nyc-trees.d/env/NYC_TREES_DB_PASSWORD) &&
psql -c "delete from django_flatpage_sites;" &&
psql -c "delete from django_flatpage;"
cd /opt/app &&
envdir /etc/nyc-trees.d/env ./manage.py make_training_flatpages'
