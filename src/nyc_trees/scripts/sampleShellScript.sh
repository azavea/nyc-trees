# !/bin/bash

# this is a sample shell script that you may want to run from a cron job

# setup the virtual environment
APP="virtualEnvironmentName" # name of the virtual environment
export WORKON_HOME=/var/virtualenvs
export PROJECT_HOME=/var/web
source /usr/local/bin/virtualenvwrapper.sh
workon $APP

python /path/to/project/manage.py your_script
