#!/bin/bash
set -ex

export NYC_TREES_TEST_DB_NAME="test_nyc_trees_$(bash -c 'echo $RANDOM')"

if [ "$SELENIUM_PLATFORM$SELENIUM_BROWSER$SELENIUM_VERSION" = "Linuxfirefox34" ]
then
  # Touchstone
  vagrant up --provision
else
  # Matrix
  vagrant up app --provision
fi

./scripts/manage.sh selenium $@
