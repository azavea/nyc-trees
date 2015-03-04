#!/bin/bash

# run a .sql file through psql on the services vm
# Works for files located at or below project root.
#
# ex:
# touch nyc_trees/foo.sql
# ./nyc_trees/scripts/psql foo.sql
#
# caveat: relative paths are a little tricky, but mostly work
#

set -e
set -x

vagrant ssh services -c "sudo su postgres -c 'psql --pset=pager=off nyc_trees -f /vagrant/$1'"
