import csv
import requests
import boto
import datetime

from troposphere import Ref, Tags, ec2

VPC_CIDR = '10.0.0.0/16'
ALLOW_ALL_CIDR = '0.0.0.0/0'

EC2_REGIONS = [
    'us-east-1'
]
EC2_AVAILABILITY_ZONES = [
    'b',
    'd'
]
EC2_INSTANCE_TYPES = [
    't1.micro',
    't2.micro',
    'm3.medium'
]
RDS_INSTANCE_TYPES = [
    'db.t2.micro',
    'db.m3.large'
]
ELASTICACHE_INSTANCE_TYPES = [
    'cache.m1.small'
]


def get_ubuntu_daily_ami_mapping(arch='amd64', root_store='ebs',
                                 virtualization='hvm'):
    """Retrieves yesterday's daily Ubuntu AMI ID for each EC2_REGIONS

    Arguments
    :param arch: Architecture preference for the AMI
    :param root_store: Root store preference for the AMI
    :param virtualization: Virtualization type preference for the AMI
    """
    response = requests.get(
        'http://cloud-images.ubuntu.com/query/trusty/server/daily.txt'
    )

    if response.status_code != 200:
        raise Exception('Ubuntu Image ID Data not found.')

    csv_data = response.text.strip().split('\n')
    yesterdays_date = (datetime.datetime.now() -
                       datetime.timedelta(days=1)).strftime("%Y%m%d")

    def get_image_id(region):
        for row in csv.reader(csv_data, delimiter='\t'):
            criteria = [
                region in row,
                arch in row,
                root_store in row,
                virtualization in row,
                yesterdays_date in row
            ]

            if all(criteria):
                return row[7]

        raise Exception('Could not find image ID for %s' % region)

    return {region: {'AMI': get_image_id(region)} for region in EC2_REGIONS}


def get_nat_ami_mapping():
    """Retrieves the most recent NAT AMI ID for each EC2_REGIONS"""
    def get_image_id(region):
        c = boto.connect_ec2()
        all_images = c.get_all_images(owners='amazon', filters={
            'name': '*ami-vpc-nat*'
        })

        images = [i for i in all_images if 'beta' not in i.name]

        return sorted(images, key=lambda i: i.name, reverse=True)[0].id

    return {region: {'AMI': get_image_id(region)} for region in EC2_REGIONS}


def create_route_table(template, name, vpc, **attrs):
    """Creates a route table as part of an existing VPC

    Arguments
    :param template: An instance of troposphere.Template
    :param name: A name for the route table
    :param vpc: An instance of troposphere.ec2.VPC
    :param **attrs: Additional arguments for troposphere.ec2.RouteTable
    """
    return template.add_resource(ec2.RouteTable(
        name,
        VpcId=Ref(vpc),
        Tags=Tags(Name=name),
        **attrs
    ))


def create_subnet(template, name, vpc, cidr_block, availability_zone):
    """Creates a subnet as part of an existing VPC

    Arguments
    :param template: An instance of troposphere.Template
    :param name: A name for the subnet
    :param cidr_block: A CIDR block for the subnet
    :param availability_zone: An availability zone for the subnet
    """
    return template.add_resource(ec2.Subnet(
        name,
        VpcId=Ref(vpc),
        CidrBlock=cidr_block,
        AvailabilityZone=availability_zone,
        Tags=Tags(Name=name)
    ))


def create_route(template, name, route_table, cidr_block=None, **attrs):
    """Creates a route as part of an existing route table

    Arguments
    :param template: An instance of troposphere.Template
    :param name: A name for the route
    :param route_table: An instance of troposphere.ec2.RouteTable
    :param cidr_block: A CIDR block for the route
    :param **attrs: Additional arguments for troposphere.ec2.route
    """
    cidr_block = cidr_block or ALLOW_ALL_CIDR
    return template.add_resource(ec2.Route(
        name,
        RouteTableId=Ref(route_table),
        DestinationCidrBlock=cidr_block,
        **attrs
    ))


def create_security_group(template, name, description, vpc, ingress,
                          egress, **attrs):
    """Creates a security group

    Arguments
    :param template: An instance of troposphere.Template
    :param name: A name for the security group
    :param description: A description for the security group
    :param vpc: An instance of troposphere.ec2.VPC
    :param ingress: An array of troposphere.ec2.SecurityGroupRules
    :param egress: An array of troposphere.ec2.SecurityGroupRules
    :param **attrs: Additional arguments for troposphere.ec2.SecurityGroup
    """
    return template.add_resource(ec2.SecurityGroup(
        name,
        GroupDescription=description,
        VpcId=Ref(vpc),
        SecurityGroupIngress=ingress,
        SecurityGroupEgress=egress,
        Tags=Tags(Name=name),
        **attrs
    ))


def validate_cloudformation_template(template_body):
    """Validates the JSON of a CloudFormation template produced by Troposphere

    Arguments
    :param template_body: The string representation of CloudFormation template
                          JSON
    """
    c = boto.connect_cloudformation()

    return c.validate_template(template_body=template_body)
