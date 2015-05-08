#!/bin/bash

# Run a celery worker interactively with debug output

set -e

STOP_SERVICE="(sudo service celery stop || /bin/true)"
CHANGE_DIR="cd /opt/app/"
RUN_CELERY="sudo -u celery envdir /etc/nyc-trees.d/env celery -A 'nyc_trees.celery:app' worker --autoreload -l debug"

vagrant ssh app -c "$STOP_SERVICE && $CHANGE_DIR && $RUN_CELERY"
