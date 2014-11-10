from troposphere import Template, Parameter, Ref, FindInMap, Output, GetAtt, \
    Join, Tags, ec2

import template_utils as utils
import troposphere.elasticloadbalancing as elb

t = Template()

t.add_version('2010-09-09')
t.add_description('A VPC stack for the nyc-trees project.')

#
# Parameters
#
keyname_param = t.add_parameter(Parameter(
    'KeyName', Type='String', Default='nyc-trees-test',
    Description='Name of an existing EC2 key pair'
))

office_cidr_param = t.add_parameter(Parameter(
    'OfficeCIDR', Type='String', Default='216.158.51.82/32',
    Description='CIDR notation of office IP addresses'
))

nat_instance_type_param = t.add_parameter(Parameter(
    'NATInstanceType', Type='String', Default='t1.micro',
    Description='NAT EC2 instance type',
    AllowedValues=utils.EC2_INSTANCE_TYPES,
    ConstraintDescription='must be a valid EC2 instance type.'
))

bastion_instance_type_param = t.add_parameter(Parameter(
    'BastionInstanceType', Type='String', Default='t2.micro',
    Description='Bastion EC2 instance type',
    AllowedValues=utils.EC2_INSTANCE_TYPES,
    ConstraintDescription='must be a valid EC2 instance type.'
))

bastion_host_ami_param = t.add_parameter(Parameter(
    'BastionHostAMI', Type='String', Default='ami-d87dc6b0',
    Description='Bastion host AMI'
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

public_route_table = utils.create_route_table(t, 'PublicRouteTable', vpc)

utils.create_route(
    t, 'PublicRoute', public_route_table, DependsOn=gateway_attachment.title,
    GatewayId=Ref(gateway)
)

nat_security_group = utils.create_security_group(
    t, 'sgNAT', 'Enables access to the NAT devices', vpc,
    ingress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', CidrIp=utils.ALLOW_ALL_CIDR, FromPort=p, ToPort=p
        )
        for p in [22, 80, 443]
    ],
    egress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', CidrIp=utils.ALLOW_ALL_CIDR, FromPort=p, ToPort=p
        )
        for p in [80, 443]
    ]
)

public_subnets = []
private_subnets = []

for index, availability_zone in enumerate(utils.EC2_AVAILABILITY_ZONES):
    if index == 1:
        index = 2

    public_subnet = utils.create_subnet(
        t, 'USEast1%sPublicSubnet' % availability_zone.upper(), vpc,
        '10.0.%s.0/24' % index, 'us-east-1%s' % availability_zone
    )

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
        Tags=Tags(Name='USEast1%sNATInstance' % availability_zone.upper())
    ))

    private_subnet = utils.create_subnet(
        t, 'USEast1%sPrivateSubnet' % availability_zone.upper(), vpc,
        '10.0.%s.0/24' % (index + 1), 'us-east-1%s' % availability_zone
    )

    private_route_table = utils.create_route_table(
        t, 'USEast1%sPrivateRouteTable' % availability_zone.upper(), vpc)

    private_route = utils.create_route(
        t, 'USEast1%sPrivateRoute' % availability_zone.upper(),
        private_route_table, InstanceId=Ref(nat_device))

    t.add_resource(ec2.SubnetRouteTableAssociation(
        '%sPrivateSubnetRouteTableAssociation' % private_subnet.title,
        SubnetId=Ref(private_subnet),
        RouteTableId=Ref(private_route_table)
    ))

    public_subnets.append(public_subnet)
    private_subnets.append(private_subnet)

bastion_security_group = utils.create_security_group(
    t, 'sgBastion', 'Enables access to the BastionHost', vpc,
    ingress=[
        ec2.SecurityGroupRule(IpProtocol='tcp', CidrIp=Ref(office_cidr_param),
                              FromPort=p, ToPort=p)
        for p in [22, 8080, 8081]
    ] + [
        ec2.SecurityGroupRule(IpProtocol='tcp', CidrIp=utils.VPC_CIDR,
                              FromPort=p, ToPort=p)
        for p in [2003, 8125, 20514]
    ] + [
        ec2.SecurityGroupRule(IpProtocol='udp', CidrIp=utils.VPC_CIDR,
                              FromPort=p, ToPort=p)
        for p in [8125]
    ],
    egress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', CidrIp=utils.VPC_CIDR, FromPort=p, ToPort=p
        )
        for p in [22, 5432, 6379]
    ] + [
        ec2.SecurityGroupRule(IpProtocol='tcp', CidrIp=utils.ALLOW_ALL_CIDR,
                              FromPort=p, ToPort=p)
        for p in [80, 443]
    ]
)

bastion_host = t.add_resource(ec2.Instance(
    'BastionHost',
    BlockDeviceMappings=[
        {
            "DeviceName": "/dev/sda1",
            "Ebs": {"VolumeSize": "128"}
        }
    ],
    InstanceType=Ref(bastion_instance_type_param),
    KeyName=Ref(keyname_param),
    ImageId=Ref(bastion_host_ami_param),
    NetworkInterfaces=[
        ec2.NetworkInterfaceProperty(
            Description='ENI for BastionHost',
            GroupSet=[Ref(bastion_security_group)],
            SubnetId=Ref(public_subnets[0]),
            AssociatePublicIpAddress=True,
            DeviceIndex=0,
            DeleteOnTermination=True
        )
    ],
    Tags=Tags(Name='BastionHost')
))

#
# Security Group Resources
#
app_server_load_balancer_security_group = utils.create_security_group(
    t, 'sgAppServerLoadBalancer',
    'Enables access to application servers via a load balancer',
    vpc,
    ingress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', CidrIp=utils.ALLOW_ALL_CIDR, FromPort=p, ToPort=p
        )
        for p in [80]
    ],
    egress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', CidrIp=utils.VPC_CIDR, FromPort=p, ToPort=p
        )
        for p in [80]
    ]
)

tile_server_load_balancer_security_group = utils.create_security_group(
    t, 'sgTileServerLoadBalancer',
    'Enables access to tile servers via a load balancer',
    vpc,
    ingress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', CidrIp=utils.ALLOW_ALL_CIDR, FromPort=p, ToPort=p
        )
        for p in [80]
    ],
    egress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', CidrIp=utils.VPC_CIDR, FromPort=p, ToPort=p
        )
        for p in [80]
    ]
)

app_server_security_group = utils.create_security_group(
    t, 'sgAppServer',
    'Enables access to application servers', vpc,
    ingress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', SourceSecurityGroupId=Ref(sg),
            FromPort=22, ToPort=22
        )
        for sg in [bastion_security_group]
    ] + [
        ec2.SecurityGroupRule(
            IpProtocol='tcp', SourceSecurityGroupId=Ref(sg),
            FromPort=80, ToPort=80
        )
        for sg in [app_server_load_balancer_security_group,
                   bastion_security_group]
    ],
    egress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', CidrIp=utils.VPC_CIDR, FromPort=p, ToPort=p
        )
        for p in [80, 2003, 5432, 6379, 8125, 20514]
    ] + [
        ec2.SecurityGroupRule(
            IpProtocol='udp', CidrIp=utils.VPC_CIDR, FromPort=p, ToPort=p
        )
        for p in [8125]
    ] + [
        ec2.SecurityGroupRule(
            IpProtocol='tcp', CidrIp=utils.ALLOW_ALL_CIDR, FromPort=p, ToPort=p
        )
        for p in [80, 443]
    ]
)

tile_server_security_group = utils.create_security_group(
    t, 'sgTileServer',
    'Enables access to tile servers', vpc,
    ingress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', SourceSecurityGroupId=Ref(sg),
            FromPort=22, ToPort=22
        )
        for sg in [bastion_security_group]
    ] + [
        ec2.SecurityGroupRule(
            IpProtocol='tcp', SourceSecurityGroupId=Ref(sg),
            FromPort=80, ToPort=80
        )
        for sg in [tile_server_load_balancer_security_group,
                   bastion_security_group]
    ],
    egress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', CidrIp=utils.VPC_CIDR, FromPort=p, ToPort=p
        )
        for p in [80, 2003, 5432, 6379, 8125, 20514]
    ] + [
        ec2.SecurityGroupRule(
            IpProtocol='udp', CidrIp=utils.VPC_CIDR, FromPort=p, ToPort=p
        )
        for p in [8125]
    ] + [
        ec2.SecurityGroupRule(
            IpProtocol='tcp', CidrIp=utils.ALLOW_ALL_CIDR, FromPort=p, ToPort=p
        )
        for p in [80, 443]
    ]
)

database_server_security_group = utils.create_security_group(
    t, 'sgDatabaseServer', 'Enables access to database servers', vpc,
    ingress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', SourceSecurityGroupId=Ref(sg),
            FromPort=5432, ToPort=5432
        )
        for sg in [bastion_security_group,
                   app_server_security_group,
                   tile_server_security_group]
    ],
    egress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', CidrIp=utils.VPC_CIDR, FromPort=p, ToPort=p
        )
        for p in [5432]
    ]
)

cache_cluster_security_group = utils.create_security_group(
    t, 'sgCacheCluster', 'Enables access to the cache cluster', vpc,
    ingress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', SourceSecurityGroupId=Ref(sg),
            FromPort=6379, ToPort=6379
        )
        for sg in [bastion_security_group,
                   app_server_security_group,
                   tile_server_security_group]
    ],
    egress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', CidrIp=utils.VPC_CIDR, FromPort=p, ToPort=p
        )
        for p in [6379]
    ]
)

#
# ELB Resources
#
app_server_load_balancer = t.add_resource(elb.LoadBalancer(
    'elbAppServer',
    LoadBalancerName='elbAppServer',
    # TODO: Create an S3 bucket automatically and enable logging.
    ConnectionDrainingPolicy=elb.ConnectionDrainingPolicy(
        Enabled=True,
        Timeout=300,
    ),
    CrossZone=True,
    SecurityGroups=[Ref(app_server_security_group)],
    Listeners=[
        elb.Listener(
            LoadBalancerPort='80',
            InstancePort='80',
            Protocol='HTTP',
        ),
    ],
    HealthCheck=elb.HealthCheck(
        Target="HTTP:80/",
        HealthyThreshold="3",
        UnhealthyThreshold="2",
        Interval="30",
        Timeout="5",
    ),
    Subnets=[Ref(s)
             for s in public_subnets],
    Tags=Tags(Name='elbAppServer')
))

tile_server_load_balancer = t.add_resource(elb.LoadBalancer(
    'elbTileServer',
    LoadBalancerName='elbTileServer',
    # TODO: Create an S3 bucket automatically and enable logging.
    ConnectionDrainingPolicy=elb.ConnectionDrainingPolicy(
        Enabled=True,
        Timeout=300,
    ),
    CrossZone=True,
    SecurityGroups=[Ref(tile_server_security_group)],
    Listeners=[
        elb.Listener(
            LoadBalancerPort='80',
            InstancePort='80',
            Protocol='HTTP',
        ),
    ],
    HealthCheck=elb.HealthCheck(
        Target="HTTP:80/",
        HealthyThreshold="3",
        UnhealthyThreshold="2",
        Interval="30",
        Timeout="5",
    ),
    Subnets=[Ref(s)
             for s in public_subnets],
    Tags=Tags(Name='elbTileServer')
))

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
        'BastionPublicIPAddress',
        Description='Public IP address of the BastionHost',
        Value=GetAtt(bastion_host.title, 'PublicIp')
    ),
    Output(
        'BastionPrivateIPAddress',
        Description='Private IP address of the BastionHost',
        Value=GetAtt(bastion_host.title, 'PrivateIp')
    ),
    Output(
        'BastionSubnet',
        Description='Subnet associated with the BastionHost',
        Value=Ref(public_subnets[0])
    ),
    Output(
        'AppServerSubnets',
        Description='A list of subnets to associate with the application '
                    'servers',
        Value=Join(',', [
            Ref(s)
            for s in private_subnets
        ])
    ),
    Output(
        'TileServerSubnets',
        Description='A list of subnets to associate with the tile servers',
        Value=Join(',', [
            Ref(s)
            for s in private_subnets
        ])
    ),
    Output(
        'DataStoreServerSubnets',
        Description='A list of subnets to associate with the data store '
                    'servers',
        Value=Join(',', [
            Ref(s)
            for s in private_subnets
        ])
    ),
    Output(
        'sgAppServer',
        Description='Application server security group',
        Value=Ref(app_server_security_group)
    ),
    Output(
        'sgTileServer',
        Description='Tile server security group',
        Value=Ref(tile_server_security_group)
    ),
    Output(
        'sgDatabaseServer',
        Description='Database server security group',
        Value=Ref(database_server_security_group)
    ),
    Output(
        'sgCacheCluster',
        Description='Cache cluster security group',
        Value=Ref(cache_cluster_security_group)
    ),
    Output(
        'AppServerLoadBalancerEndpoint',
        Description='Application servers endpoint',
        Value=GetAtt(app_server_load_balancer, 'DNSName')
    ),
    Output(
        'TileServerLoadBalancerEndpoint',
        Description='Tile server endpoint',
        Value=GetAtt(tile_server_load_balancer, 'DNSName')
    )
])

if __name__ == '__main__':
    utils.validate_cloudformation_template(t.to_json())

    file_name = __file__.replace('.py', '.json')

    with open(file_name, 'w') as f:
        f.write(t.to_json())

    print('Template validated and written to %s' % file_name)
