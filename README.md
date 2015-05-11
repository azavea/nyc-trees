nyc-trees
=========

NYC Parks Trees Count! 2015 tree census

## Local Development

A combination of Vagrant 1.5+ and Ansible 1.8+ is used to setup the development environment for this project. It of the following virtual machines:

- `app`
- `tiler`
- `services`

The `app` virtual machine contains an instance of the Django application, `tiler` contains a tiling server, and `services` contains shared resources of `app` and `tiler`:

- PostgreSQL
- Redis
- Logstash
- Kibana
- Graphite
- Statsite

Use the following command to bring up a local development environment:

```bash
$ vagrant up
```

After provisioning is complete, you can login to the application server to execute Django management commands:

```bash
$ vagrant ssh app
vagrant@app:~$ envdir /etc/nyc-trees.d/env /opt/app/manage.py test
```

**Note**: If you get an error that resembles the following, try logging into the `app` virtual machine again for the group permissions changes to take effect:

```
envdir: fatal: unable to switch to directory /etc/nyc-trees.d/env: access denied
```

### Ports

The Vagrant configuration maps the following host ports to services
running in the VMs. You can change the host port numbers by setting
the environment variables listed in the ``Env Variable Override``
column.

Service                | Port  | URL
---------------------- | ----- | ------------------------------------------------
Django Web Application | 8000  | [http://localhost:8000](http://localhost:8000)
Graphite Dashboard     | 8080  | [http://localhost:8080](http://localhost:8080)
Kibana Dashboard       | 15601 | [http://localhost:15601](http://localhost:15601)
Tasseo                 | 15000 | [http://localhost:15000](http://localhost:15000)
PostgreSQL             | 15432 |
pgweb                  | 15433 | [http://localhost:15433](http://localhost:15433)
Redis                  | 16379 | `redis-cli -h localhost 16379`
livereload             | 35729 | (for gulp watch)
LiveServer Tests       | 9001  | (for Sauce Labs)
Testem                 | 7357  |


### JavaScript and CSS

The main tool used is [gulp](http://gulpjs.com/), which is exposed through `npm run` to avoid version conflicts.

 - To create JS bundles, compile sass, and concatenate third-party css, minify CSS and JS, and version files using `gulp-rev-all`, use `gulp` or `npm run build`.
 - To do the above but skip minification and versioning, use `gulp build --debug` or `npm run build-debug`.
 - To watch files and automatically rebuild the JS or sass files when they change, use `gulp watch --debug` or `npm run watch`.  This will also start a [livereload server](http://livereload.com/).

`gulp build` and `gulp watch` without the `--debug` flag are intentionally not exposed through `npm run`.

### Caching

In order to speed up things up, you may want to consider using a local caching proxy. The `VAGRANT_PROXYCONF_ENDPOINT` environment variable provides a way to supply a caching proxy endpoint for the virtual machines to use:

```bash
$ VAGRANT_PROXYCONF_ENDPOINT="http://192.168.96.10:8123/" vagrant up
```

## Data

See ``src/nyc_trees/apps/survey/fixtures/README.md`` for documentation on how the source data fixtures were created.

## Testing

In order to simulate the testing environment used in CI, bring up the testing environment with:

```
$ VAGRANT_ENV="TEST" vagrant up
```

Once that is complete, execute the top-level test suite responsible for linting and unit testing the client and server-side components:

```bash
$ ./scripts/test.sh
```

If you want to run the integration tests, use the following command:

```bash
$ ./scripts/manage.sh selenium
```

In addition, other [scripts](scripts/) exist if you want to test just one of the client or server-side components.

## Deployment

For more details around the Amazon Web Services deployment process, please see the deployment [README](deployment/README.md).d
