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
$ export AWS_SSL_CERTIFICATE_ID=ASC...
$ export AWS_PUBLIC_HOSTED_ZONE=treescount.nycgovparks.org
$ export AWS_APP_INSTANCE_TYPE=m3.medium
$ export AWS_TILE_INSTANCE_TYPE=m3.medium
$ export NYC_TREES_DB_PASSWORD=***
```

Lastly, install the AWS CLI, Boto, and Troposphere:

```bash
$ cd deployment
$ pip install -r deployment/requirements.txt
```

## S3 Website Failover

In the event that all application servers fail simultaneously, Route 53 DNS handles failing over to an S3 static website. The contents of the failover site are located in `src/failover_website`, from the project root.

In order for the failover process to complete successfully, an [S3 website enabled bucket](http://docs.aws.amazon.com/AmazonS3/latest/dev/HowDoIWebsiteConfiguration.html) needs to exist on the AWS account that the application is being deployed to. The name of the bucket must be the same name as `AWS_PUBLIC_HOSTED_ZONE` (this ensures that the S3 website can use it as a custom domain). A CloudFront distribution fronts the contents of the S3 website for HTTPS compatibility with the application server endpoint.

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
