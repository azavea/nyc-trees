#!/bin/bash

set -e
set -x

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
FIXTURE="$DIR/../src/nyc_trees/apps/survey/fixtures/blockface.json"

vagrant ssh app -c "cd /opt/app && envdir /etc/nyc-trees.d/env ./manage.py dumpdata survey.Blockface" > $FIXTURE
