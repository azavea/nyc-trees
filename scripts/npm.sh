#!/bin/bash

# Pass arguments to 'npm' at the project root

set -e
set -x

vagrant ssh app -c "cd /opt/app && npm $*"
