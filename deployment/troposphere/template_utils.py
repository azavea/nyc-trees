import boto

VPC_CIDR = '10.0.0.0/16'
ALLOW_ALL_CIDR = '0.0.0.0/0'
OFFICE_CIDR = '216.158.51.82/32'

EC2_REGIONS = [
    'us-east-1'
]
EC2_AVAILABILITY_ZONES = [
    'a',
    'd'
]
EC2_INSTANCE_TYPES = [
    # T2
    't2.micro',
    't2.small',
    't2.medium',
    # M3
    'm3.medium',
    'm3.large',
    'm3.xlarge',
    'm3.2xlarge',
]
RDS_INSTANCE_TYPES = [
    # T2
    'db.t2.micro',
    'db.t2.small',
    'db.t2.medium',
    # M3
    'db.m3.medium',
    'db.m3.large',
    'db.m3.xlarge',
    'db.m3.2xlarge',
]
ELASTICACHE_INSTANCE_TYPES = [
    # T2
    'cache.t2.micro',
    'cache.t2.small',
    'cache.t2.medium',
    # M1
    'cache.m1.small',
    # M3
    'cache.m3.medium',
    'cache.m3.large',
    'cache.m3.xlarge',
    'cache.m3.2xlarge',
]

S3_US_STANDARD_HOSTED_ZONE_ID = 'Z3AQBSTGFYJSTF'
S3_US_STANDARD_HOSTED_ZONE_ALIAS_TARGET = 's3-website-us-east-1.amazonaws.com'

CLOUDFRONT_HOSTED_ZONE_ID = 'Z2FDTNDATAQYW2'


def get_nat_ami_mapping():
    """Retrieves the most recent NAT AMI ID for each EC2_REGIONS"""
    def get_image_id(region):
        c = boto.connect_ec2()
        all_images = c.get_all_images(owners='amazon', filters={
            'name': '*ami-vpc-nat-hvm*'
        })

        images = [i for i in all_images if 'beta' not in i.name]

        return sorted(images, key=lambda i: i.name, reverse=True)[0].id

    return {region: {'AMI': get_image_id(region)} for region in EC2_REGIONS}


def read_file(file_name):
    """Reads an entire file and returns it as a string
    Arguments
    :param file_name: A path to a file
    """
    with open(file_name, 'r') as f:
        return f.read()


def validate_cloudformation_template(template_body):
    """Validates the JSON of a CloudFormation template produced by Troposphere

    Arguments
    :param template_body: The string representation of CloudFormation template
                          JSON
    """
    c = boto.connect_cloudformation()

    return c.validate_template(template_body=template_body)
