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
    't2.micro',
    't2.medium',
    'm3.medium',
    'm3.large'
]
RDS_INSTANCE_TYPES = [
    'db.t2.micro',
    'db.m3.large'
]
ELASTICACHE_INSTANCE_TYPES = [
    'cache.t2.small',
    'cache.m1.small'
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


def validate_cloudformation_template(template_body):
    """Validates the JSON of a CloudFormation template produced by Troposphere

    Arguments
    :param template_body: The string representation of CloudFormation template
                          JSON
    """
    c = boto.connect_cloudformation()

    return c.validate_template(template_body=template_body)
