from troposphere import Template, Parameter, Ref, FindInMap, Output, Join, \
    Tags, ec2

import template_utils as utils

t = Template()

t.add_version('2010-09-09')
t.add_description('A VPC stack for the nyc-trees project.')

#
# Parameters
#
keyname_param = t.add_parameter(Parameter(
    'KeyName', Type='String', Default='nyc-trees-stg',
    Description='Name of an existing EC2 key pair'
))

nat_instance_type_param = t.add_parameter(Parameter(
    'NATInstanceType', Type='String', Default='t2.micro',
    Description='NAT EC2 instance type',
    AllowedValues=utils.EC2_INSTANCE_TYPES,
    ConstraintDescription='must be a valid EC2 instance type.'
))

#
# Mappings
#
t.add_mapping('NATAMIMap', utils.get_nat_ami_mapping())

#
# VPC Resources
#
vpc = t.add_resource(ec2.VPC(
    'NYCTreesVPC', CidrBlock=utils.VPC_CIDR, EnableDnsSupport=True,
    EnableDnsHostnames=True,
    Tags=Tags(Name='NYCTreesVPC')
))

gateway = t.add_resource(ec2.InternetGateway(
    'InternetGateway', Tags=Tags(Name='InternetGateway')
))

gateway_attachment = t.add_resource(ec2.VPCGatewayAttachment(
    'VPCGatewayAttachment', VpcId=Ref(vpc), InternetGatewayId=Ref(gateway)
))

public_route_table = t.add_resource(ec2.RouteTable(
    'PublicRouteTable', VpcId=Ref(vpc), Tags=Tags(Name='PublicRouteTable')
))

t.add_resource(ec2.Route(
    'PublicRoute', RouteTableId=Ref(public_route_table),
    DestinationCidrBlock=utils.ALLOW_ALL_CIDR,
    DependsOn=gateway_attachment.title, GatewayId=Ref(gateway)
))

#
# Security Group Resources
#
nat_security_group = t.add_resource(ec2.SecurityGroup(
    'sgNAT', GroupDescription='Enables access to the NAT devices',
    VpcId=Ref(vpc),
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', CidrIp=utils.ALLOW_ALL_CIDR, FromPort=p, ToPort=p
        )
        for p in [22, 80, 443]
    ],
    SecurityGroupEgress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', CidrIp=utils.ALLOW_ALL_CIDR, FromPort=p, ToPort=p
        )
        for p in [80, 443]
    ],
    Tags=Tags(Name='sgNAT')
))

public_subnets = []
private_subnets = []

for index, availability_zone in enumerate(utils.EC2_AVAILABILITY_ZONES):
    if index == 1:
        index = 2

    public_subnet = t.add_resource(ec2.Subnet(
        'USEast1%sPublicSubnet' % availability_zone.upper(), VpcId=Ref(vpc),
        CidrBlock='10.0.%s.0/24' % index,
        AvailabilityZone='us-east-1%s' % availability_zone,
        Tags=Tags(Name='USEast1%sPublicSubnet' % availability_zone.upper())
    ))

    t.add_resource(ec2.SubnetRouteTableAssociation(
        '%sPublicRouteTableAssociation' % public_subnet.title,
        SubnetId=Ref(public_subnet),
        RouteTableId=Ref(public_route_table)
    ))

    nat_device = t.add_resource(ec2.Instance(
        'USEast1%sNATDevice' % availability_zone.upper(),
        InstanceType=Ref(nat_instance_type_param),
        KeyName=Ref(keyname_param),
        SourceDestCheck=False,
        ImageId=FindInMap('NATAMIMap', Ref('AWS::Region'), 'AMI'),
        NetworkInterfaces=[
            ec2.NetworkInterfaceProperty(
                Description='ENI for NATDevice',
                GroupSet=[Ref(nat_security_group)],
                SubnetId=Ref(public_subnet),
                AssociatePublicIpAddress=True,
                DeviceIndex=0,
                DeleteOnTermination=True,
            )
        ],
        Tags=Tags(Name='NATDevice')
    ))

    private_subnet = t.add_resource(ec2.Subnet(
        'USEast1%sPrivateSubnet' % availability_zone.upper(), VpcId=Ref(vpc),
        CidrBlock='10.0.%s.0/24' % (index + 1),
        AvailabilityZone='us-east-1%s' % availability_zone,
        Tags=Tags(Name='USEast1%sPrivateSubnet' % availability_zone.upper())
    ))

    private_route_table = t.add_resource(ec2.RouteTable(
        'USEast1%sPrivateRouteTable' % availability_zone.upper(),
        VpcId=Ref(vpc),
        Tags=Tags(
            Name='USEast1%sPrivateRouteTable' % availability_zone.upper()
        )
    ))

    private_route = t.add_resource(ec2.Route(
        'USEast1%sPrivateRoute' % availability_zone.upper(),
        RouteTableId=Ref(private_route_table),
        DestinationCidrBlock=utils.ALLOW_ALL_CIDR, InstanceId=Ref(nat_device)
    ))

    t.add_resource(ec2.SubnetRouteTableAssociation(
        '%sPrivateSubnetRouteTableAssociation' % private_subnet.title,
        SubnetId=Ref(private_subnet),
        RouteTableId=Ref(private_route_table)
    ))

    public_subnets.append(public_subnet)
    private_subnets.append(private_subnet)

#
# Outputs
#
t.add_output([
    Output(
        'VpcId',
        Description='VPC ID',
        Value=Ref(vpc)
    ),
    Output(
        'PublicSubnets',
        Description='A list of public subnets',
        Value=Join(',', [
            Ref(s)
            for s in public_subnets
        ])
    ),
    Output(
        'PrivateSubnets',
        Description='A list of private subnets',
        Value=Join(',', [
            Ref(s)
            for s in private_subnets
        ])
    ),
])

if __name__ == '__main__':
    utils.validate_cloudformation_template(t.to_json())

    file_name = __file__.replace('.py', '.json')

    with open(file_name, 'w') as f:
        f.write(t.to_json())

    print('Template validated and written to %s' % file_name)
