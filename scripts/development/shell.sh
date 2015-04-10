#!/bin/bash

# open a bash shell at the project root on vm with env vars loaded

set -e

vagrant ssh app -c "cd /opt/app && envdir /etc/nyc-trees.d/env bash"
