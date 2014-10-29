.PHONY: runserver test

test:
	vagrant ssh app -c "envdir /etc/nyc-trees.d/env /opt/app/manage.py test $(TEST_ARGS)"

runserver:
	vagrant ssh app -c "envdir /etc/nyc-trees.d/env /opt/app/manage.py runserver 0.0.0.0:8000"
