#!/bin/bash

set -e
set -x

ARGS=$*

# Sane defaults for runserver
if [[ $# -eq 1 ]] && [[ $1 == "runserver" ]]; then
    ARGS="runserver 0.0.0.0:8000"
fi

vagrant ssh app -c "envdir /etc/nyc-trees.d/env /opt/app/manage.py $ARGS"
