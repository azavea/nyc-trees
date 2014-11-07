#!/bin/bash

set -e
set -x

vagrant ssh app -c "envdir /etc/nyc-trees.d/env /opt/app/manage.py $*"
