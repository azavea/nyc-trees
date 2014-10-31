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
vagrant@app:~$ envdir /etc/nyc-trees.d/env /opt/app/manage.py runserver
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
$ pip install -r deployment/requirements.txt
```

Then, generate all of the CloudFormation templates:

```bash
$ cd deployment
$ make
```

### Launch the AWS Virtual Private Cloud (VPC)

From within the `deployment` directory, create the VPC CloudFormation stack:

```
$ make vpc-stack
```

### Launch the Data Store Servers

When the VPC stack is complete, create the data store CloudFormation stack:

```
$ make data-store-stack
```

### Create Private DNS stack

After the data store stack is complete, create the private DNS stack:

```
$ make private-dns-stack
```

### Create Monitoring Server AMI

Now that both the VPC, data store, and private DNS stacks are complete, we can generate the monitoring server AMI. This needs to occur *after* the data store stack is complete because Redis (part of the data store stack) is used as a buffer for inbound messages into Logstash:

```
$ make monitoring-ami
```

After the monitoring server AMI is created, we need to update the VPC and private DNS stacks so that the bastion host uses the new monitoring server AMI. The bastion host has dual roles (VPC bastion and monitoring server):

```
$ make update-vpc-stack
$ make update-private-dns-stack
```

### Launch the Tile and Application Servers

Now that the VPC, data store, and monitoring stacks are setup, we can begin working on the tile and applications servers. First, we need to create their AMIs:

```
$ make app-and-tiler-amis
```

Next, we can create each server stack, which will make use of the most recent AMIs available:

```
$ make tiler-stack
$ make app-stack
```
