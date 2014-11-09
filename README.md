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

After provisioning is complete, you can bring up the Django `runserver` from within the `app` virtual machine with the following commands:

```bash
$ vagrant ssh app
vagrant@app:~$ envdir /etc/nyc-trees.d/env /opt/app/manage.py runserver 0.0.0.0:8000
```

**Note**: If you get an error that resembles the following, try logging into the `app` virtual machine again for the group permissions changes to take effect:

```
envdir: fatal: unable to switch to directory /etc/nyc-trees.d/env: access denied
```

### Caching

In order to speed up things up, you may want to consider using a local caching proxy. The `VAGRANT_PROXYCONF_ENDPOINT` environmental variable provides a way to supply a caching proxy endpoint for the virtual machines to use:

```bash
$ VAGRANT_PROXYCONF_ENDPOINT="http://192.168.96.10:8123/" vagrant up
```

### Log Aggregation

In order to view the Kibana web UI, navigate to the following URL from a browser on the virtual machine host:

```
http://localhost:8081/index.html#/dashboard/file/logstash.json
```

## Deployment

Deployment is driven by the [Amazon Web Services CLI](http://aws.amazon.com/cli/), but expects the following resources to exist in the target AWS account:

- An EC2 key pair
- Access keys to sign API requests
- An IAM role for the application and tile servers
- An SNS topic for global notifications

In order to get started, install the deployment dependencies:

```bash
$ pip install -r deployment/troposphere/requirements.txt
```

Then, generate all of the CloudFormation templates:

```bash
$ cd deployment/troposphere
$ make
```

### Launch the AWS Virtual Private Cloud

From the root of the repository, submit the CloudFormation stack template to AWS:

```
$ aws cloudformation create-stack --profile nyc-trees-test --stack-name NYCTreesVPC \
--parameters file://deployment/troposphere/parameters/staging_vpc.json \
--template-body file://deployment/troposphere/vpc_template.json
```

### Launch the Data Store Servers

First, update the following parameters for the CloudFormation data store stack in `deployment/troposphere/parameters/staging_data_store.json`:

- `GlobalNotificationsARN`: One of the prerequisites listed above
- `sgDatabaseServer`: Created by the VPC stack
- `sgCacheCluster`: Created by the VPC stack
- `DataStoreServerSubnets`: Created by the VPC stack (private subnets)

Then, launch the apply the tile server stack template:

```
$ aws cloudformation create-stack --profile nyc-trees-test --stack-name NYCTreesDataStores \
--parameters file://deployment/troposphere/parameters/staging_data_store.json \
--template-body file://deployment/troposphere/data_store_template.json
```

### Launch the Application Servers

First, update the following parameters for the CloudFormation application stack in `deployment/troposphere/parameters/staging_app.json`:

- `GlobalNotificationsARN`: One of the prerequisites listed above
- `AppServerInstanceProfile`: One of the prerequisites listed above
- `elbAppServer` - Created by the VPC stack
- `sgAppServer` - Created by the VPC stack
- `AppServerSubnets`: Created by the VPC stack (public subnets)

Then, launch the application server stack template:

```
$ aws cloudformation create-stack --profile nyc-trees-test --stack-name NYCTreesAppServers \
--parameters file://deployment/troposphere/parameters/staging_app.json \
--template-body file://deployment/troposphere/app_template.json
```

### Launch the Tile Servers

First, update the following parameters for the CloudFormation tiler stack in `deployment/troposphere/parameters/staging_tiler.json`:

- `GlobalNotificationsARN`: One of the prerequisites listed above
- `TileServerInstanceProfile`: One of the prerequisites listed above
- `elbTileServer` - Created by the VPC stack
- `sgTileServer` - Created by the VPC stack
- `TileServerSubnets`: Created by the VPC stack (public subnets)

Then, launch the apply the tile server stack template:

```
$ aws cloudformation create-stack --profile nyc-trees-test --stack-name NYCTreesTileServers \
--parameters file://deployment/troposphere/parameters/staging_tiler.json \
--template-body file://deployment/troposphere/tiler_template.json
```
