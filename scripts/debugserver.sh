#!/bin/bash

# Run a gunicorn webserver with expanded logging and auto-restart

set -e
set -x

vagrant ssh app -c "sudo service nyc-trees-app stop || /bin/true"
vagrant ssh app -c "cd /opt/app/ && envdir /etc/nyc-trees.d/env gunicorn --config /etc/nyc-trees.d/gunicorn.py nyc_trees.wsgi"
