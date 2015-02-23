# Amazon Web Services Deployment

Deployment is driven by [Packer](https://www.packer.io), [Troposphere](https://github.com/cloudtools/troposphere), and the [Amazon Web Services CLI](http://aws.amazon.com/cli/).

## Dependencies

The deployment process expects the following environment variables to be overridden:

```bash
$ export AWS_DEFAULT_PROFILE=nyc-trees-stg
$ export AWS_PROFILE=nyc-trees-stg
$ export AWS_DEFAULT_OUTPUT=text
$ export AWS_DEFAULT_REGION=us-east-1
$ export AWS_SNS_TOPIC=arn:aws:sns:us-east-1...
$ export AWS_SSL_CERTIFICATE=arn:aws:iam...
$ export AWS_PUBLIC_HOSTED_ZONE=treescount.nycgovparks.org
```

Lastly, install the AWS CLI, Boto, and Troposphere:

```bash
$ cd deployment
$ pip install -r deployment/requirements.txt
```

## Amazon Machine Images (AMIs)

In order to generate AMIs for the application, tile, and monitoring servers, use the following `make` targets:

```bash
$ make app-ami
$ make tiler-ami
$ make monitoring-ami
```

## CloudFormation (via Troposphere)

After at least one AMI of each type exists, use the following command to generate all of the CloudFormation templates:

```bash
$ make build
```

### Launch the AWS Virtual Private Cloud (VPC)

Use the following command to create the VPC stack:

```
$ make vpc-stack
```

### Create Route 53 Private Hosted Zones

Next, create the internal to the VPC private hosted zones:

```bash
$ make private-hosted-zones
```

### Launch the Data Stores

After the private hosted zones exist, create the data store stack:

```
$ make data-store-stack
```

### Launch the Tile Servers

Now that the VPC and data store stacks are setup, we can launch the tile server stack, which will make use of the most recent AMIs available:

```
$ make tiler-stack
```

### Activate Tile Servers

Depending on which color stack you just deployed (Blue or Green), activate DNS for the hosted zone:

```
$ make tiler-stack-[green,blue]
```

### Launch the Application Servers

Next, launch the application server stack, which will also make use of the most recent AMIs available:

```
$ make app-stack
```

### Activate Application Servers

Depending on which color stack you just deployed (Blue or Green), activate DNS for the hosted zone:

```
$ make app-stack-[green,blue]
```
