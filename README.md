nyc-trees
=========

NYC Parks Trees Count! 2015 tree census

## Local Development

A combination of Vagrant 1.5+ and Ansible 1.6+ is used to setup the development environment for this project. It of the following virtual machines:

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

Service                | Port  | URL                                              | Env Variable Override
---------------------- | ----- | ------------------------------------------------ | ---------------------
Django Web Application | 8000  | [http://localhost:8000](http://localhost:8000)   | NYC_TREES_PORT_8000
Graphite Dashboard     | 8080  | [http://localhost:8080](http://localhost:8080)   | NYC_TREES_PORT_8080
Kibana Dashboard       | 15601 | [http://localhost:15601](http://localhost:15601) | NYC_TREES_PORT_5601
PostgreSQL             | 15432 |                                                  | NYC_TREES_PORT_5432
pgweb                  | 15433 | [http://localhost:15433](http://localhost:15433) | NYC_TREES_PORT_5433
Redis                  | 16379 | `redis-cli -h localhost 16379`                   | NYC_TREES_PORT_6379
livereload             | 35729 | (for gulp watch)                                 | N/A
LiveServer Tests       | 9001  | (for Sauce Labs)                                 | NYC_TREES_PORT_9001
Testem                 | 7357  |                                                  | NYC_TREES_PORT_7357


### JavaScript and CSS

The main tool used is [gulp](http://gulpjs.com/), which is exposed through `npm run` to avoid version conflicts.

 - To create JS bundles, compile sass, and concatenate third-party css, minify CSS and JS, and version files using `gulp-rev-all`, use `gulp` or `npm run build`.
 - To do the above but skip minification and versioning, use `gulp build --debug` or `npm run build-debug`.
 - To watch files and automatically rebuild the JS or sass files when they change, use `gulp watch --debug` or `npm run watch`.  This will also start a [livereload server](http://livereload.com/).

`gulp build` and `gulp watch` without the `--debug` flag are intentionally not exposed through `npm run`.

### Caching

In order to speed up things up, you may want to consider using a local caching proxy. The `VAGRANT_PROXYCONF_ENDPOINT` environmental variable provides a way to supply a caching proxy endpoint for the virtual machines to use:

```bash
$ VAGRANT_PROXYCONF_ENDPOINT="http://192.168.96.10:8123/" vagrant up
```

### Log Aggregation

In order to view the Kibana web UI, navigate to the following URL from a browser on the virtual machine host:

```
http://localhost:5601/
```

### Statistics Aggregation

In order to view the Graphite Web UI, navigate to the following URL from a browser on the virtual machine host:

```
http://localhost:8080/
```

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

Deployment is driven by [Packer](https://www.packer.io), [Troposphere](https://github.com/cloudtools/troposphere), and the [Amazon Web Services CLI](http://aws.amazon.com/cli/).

### Dependencies

The deployment process expects the following resources to exist in the target AWS account:

- An EC2 key pair exported as `AWS_KEY_NAME`
- Access keys to sign API requests exported as `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
- An SNS topic for global notifications exported as `AWS_SNS_TOPIC`

In addition, export the following environmental variables for the AWS CLI:

```bash
$ export AWS_DEFAULT_OUTPUT=text
$ export AWS_DEFAULT_REGION=us-east-1
```

Lastly, install the AWS CLI, Boto, and Troposphere:

```bash
$ cd deployment
$ pip install -r deployment/requirements.txt
```

### Amazon Machine Images (AMIs)

In order to generate AMIs for the application, tile, and monitoring servers, use the following `make` targets:

```bash
$ make app-ami
$ make tiler-ami
$ make monitoring-ami
```

### CloudFormation (via Troposphere)

After at least one AMI of each type exists, use the following command to generate all of the CloudFormation templates:

```bash
$ make build
```

#### Launch the AWS Virtual Private Cloud (VPC)

Use the following command to create the VPC stack:

```
$ make vpc-stack
```

#### Create Route 53 Private Hosted Zones

Next, create the internal to the VPC private hosted zones:

```bash
$ make private-hosted-zones
```

#### Launch the Data Stores

After the private hosted zones exist, create the data store stack:

```
$ make data-store-stack
```

#### Launch the Tile and Application Servers

Now that the VPC and data store stacks are setup, we can launch the tile and applications server stacks, which will make use of the most recent AMIs available:

```
$ make tiler-stack
$ make app-stack
```
