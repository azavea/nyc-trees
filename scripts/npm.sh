#!/bin/bash

set -e
set -x

vagrant ssh app -c "cd /opt/app && npm $*"
