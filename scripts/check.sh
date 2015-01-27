#!/bin/bash

set -e
set -x

# Run flake8 against the Django codebase and output a known string so that
# the Jenkins text finder plugin can detect a failed check and mark the build
# unstable. This command should only fail the build if the `vagrant ssh`
# command itself fails.
vagrant ssh app -c "flake8 /opt/app/apps --exclude migrations || echo flake8 check failed"
