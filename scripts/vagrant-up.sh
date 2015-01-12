#!/bin/bash

DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)

source "${DIR}/vagrant-env.sh"

vagrant up --no-provision

for vm in services tiler app;
do
  with_backoff vagrant provision ${vm}
done
