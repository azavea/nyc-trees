from troposphere import Template, Parameter, Ref, Tags, GetAtt, Select, Join, \
    ec2

import template_utils as utils
import troposphere.rds as rds
import troposphere.route53 as r53
import troposphere.elasticache as ec

t = Template()

t.add_version('2010-09-09')
t.add_description('A data store stack for the nyc-trees project.')

#
# Parameters
#
hosted_zone_name_param = t.add_parameter(Parameter(
    'PublicHostedZone', Type='String',
    Default='treescount.azavea.com',
    Description='Hosted zone name for public DNS'
))

vpc_param = t.add_parameter(Parameter(
    'VpcId', Type='String', Description='Name of an existing VPC'
))

keyname_param = t.add_parameter(Parameter(
    'KeyName', Type='String', Default='nyc-trees-stg',
    Description='Name of an existing EC2 key pair'
))

notification_arn_param = t.add_parameter(Parameter(
    'GlobalNotificationsARN', Type='String',
    Description='Physical resource ID of an AWS::SNS::Topic for notifications'
))

bastion_instance_type_param = t.add_parameter(Parameter(
    'BastionInstanceType', Type='String', Default='t2.medium',
    Description='Bastion EC2 instance type',
    AllowedValues=utils.EC2_INSTANCE_TYPES,
    ConstraintDescription='must be a valid EC2 instance type.'
))

bastion_host_ami_param = t.add_parameter(Parameter(
    'BastionHostAMI', Type='String', Description='Bastion host AMI'
))

database_server_instance_type_param = t.add_parameter(Parameter(
    'DatabaseServerInstanceType', Type='String', Default='db.t2.micro',
    Description='Database server RDS instance type',
    AllowedValues=utils.RDS_INSTANCE_TYPES,
    ConstraintDescription='must be a valid RDS instance type.'
))

database_server_master_username_param = t.add_parameter(Parameter(
    'DatabaseServerMasterUsername', Type='String', Default='nyctrees',
    Description='Database server master username'
))

database_server_master_password_param = t.add_parameter(Parameter(
    'DatabaseServerMasterPassword', Type='String', Default='nyctrees',
    NoEcho=True, Description='Database server master password'
))

cache_cluster_instance_type_param = t.add_parameter(Parameter(
    'CacheClusterInstanceType', Type='String', Default='cache.m1.small',
    Description='Cache cluster ElastiCache instances type',
    AllowedValues=utils.ELASTICACHE_INSTANCE_TYPES,
    ConstraintDescription='must be a valid ElastiCache instance type.'
))

cache_cluster_endpoint_param = t.add_parameter(Parameter(
    'CacheClusterEndpoint', Type='String', Default='google.com',
    Description='Cache cluster endpoint'
))

public_subnets_param = t.add_parameter(Parameter(
    'PublicSubnets', Type='CommaDelimitedList',
    Description='A list of public subnets'
))

private_subnets_param = t.add_parameter(Parameter(
    'PrivateSubnets', Type='CommaDelimitedList',
    Description='A list of private subnets'
))

#
# Security Group Resources
#
bastion_security_group = t.add_resource(ec2.SecurityGroup(
    'sgBastion', GroupDescription='Enables access to the BastionHost',
    VpcId=Ref(vpc_param),
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(IpProtocol='tcp', CidrIp=utils.OFFICE_CIDR,
                              FromPort=p, ToPort=p)
        for p in [22, 5000, 5601, 8080]
    ] + [
        ec2.SecurityGroupRule(IpProtocol='tcp', CidrIp=utils.VPC_CIDR,
                              FromPort=p, ToPort=p)
        for p in [2003, 8125, 20514]
    ] + [
        ec2.SecurityGroupRule(IpProtocol='udp', CidrIp=utils.VPC_CIDR,
                              FromPort=p, ToPort=p)
        for p in [8125]
    ],
    SecurityGroupEgress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', CidrIp=utils.VPC_CIDR, FromPort=p, ToPort=p
        )
        for p in [22, 5432, 6379]
    ] + [
        ec2.SecurityGroupRule(IpProtocol='tcp', CidrIp=utils.ALLOW_ALL_CIDR,
                              FromPort=p, ToPort=p)
        for p in [80, 443]
    ],
    Tags=Tags(Name='sgBastion')
))

database_server_security_group = t.add_resource(ec2.SecurityGroup(
    'sgDatabaseServer',
    GroupDescription='Enables access to database servers',
    VpcId=Ref(vpc_param),
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', CidrIp=utils.VPC_CIDR, FromPort=p, ToPort=p
        )
        for p in [5432]
    ],
    SecurityGroupEgress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', CidrIp=utils.VPC_CIDR, FromPort=p, ToPort=p
        )
        for p in [5432]
    ],
    Tags=Tags(Name='sgDatabaseServer')
))

cache_cluster_security_group = t.add_resource(ec2.SecurityGroup(
    'sgCacheCluster',
    GroupDescription='Enables access to the cache cluster',
    VpcId=Ref(vpc_param),
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', CidrIp=utils.VPC_CIDR, FromPort=p, ToPort=p
        )
        for p in [6379]
    ],
    SecurityGroupEgress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', CidrIp=utils.VPC_CIDR, FromPort=p, ToPort=p
        )
        for p in [6379]
    ],
    Tags=Tags(Name='sgCacheCluster')
))

#
# Bastion Resources
#
bastion_host = t.add_resource(ec2.Instance(
    'BastionHost',
    BlockDeviceMappings=[
        {
            "DeviceName": "/dev/sda1",
            "Ebs": {
                "VolumeType": "gp2",
                "VolumeSize": "256"
            }
        }
    ],
    InstanceType=Ref(bastion_instance_type_param),
    KeyName=Ref(keyname_param),
    ImageId=Ref(bastion_host_ami_param),
    NetworkInterfaces=[
        ec2.NetworkInterfaceProperty(
            Description='ENI for BastionHost',
            GroupSet=[Ref(bastion_security_group)],
            SubnetId=Select("0", Ref(public_subnets_param)),
            AssociatePublicIpAddress=True,
            DeviceIndex=0,
            DeleteOnTermination=True
        )
    ],
    Tags=Tags(Name='BastionHost')
))

#
# RDS Resources
#
database_server_subnet_group = t.add_resource(rds.DBSubnetGroup(
    "dbsngDatabaseServer",
    DBSubnetGroupDescription='Private subnets for the RDS instances',
    SubnetIds=Ref(private_subnets_param),
    Tags=Tags(Name='dbsngDatabaseServer')
))

database_server_instance = t.add_resource(rds.DBInstance(
    "DatabaseServer",
    AllocatedStorage=20,
    AllowMajorVersionUpgrade=False,
    AutoMinorVersionUpgrade=True,
    BackupRetentionPeriod=30,
    DBInstanceClass=Ref(database_server_instance_type_param),
    DBInstanceIdentifier='nyctrees-nyc-trees-database-server',
    DBName='nyc_trees',
    DBSubnetGroupName=Ref(database_server_subnet_group),
    Engine='postgres',
    EngineVersion='9.3.5',
    MasterUsername=Ref(database_server_master_username_param),
    MasterUserPassword=Ref(database_server_master_password_param),
    MultiAZ=True,
    PreferredBackupWindow='01:00-01:30',  # 9:00-9:30PM ET
    PreferredMaintenanceWindow='mon:01:30-mon:02:30',  # 9:30PM-10:30PM ET
    VPCSecurityGroups=[Ref(database_server_security_group)],
    Tags=Tags(Name='DatabaseServer')
))

#
# ElastiCache Resources
#
cache_cluster_subnet_group = t.add_resource(ec.SubnetGroup(
    "ecsngCacheCluster",
    Description='Private subnets for the ElastiCache instances',
    SubnetIds=Ref(private_subnets_param)
))

cache_cluster_parameter_group = t.add_resource(ec.ParameterGroup(
    'ecpgCacheCluster',
    CacheParameterGroupFamily='redis2.8',
    Description='Parameter group for the ElastiCache instances',
    Properties={
        "appendonly": "yes"
    }
))

cache_cluster = t.add_resource(ec.CacheCluster(
    'CacheCluster',
    AutoMinorVersionUpgrade=True,
    CacheNodeType=Ref(cache_cluster_instance_type_param),
    CacheParameterGroupName=Ref(cache_cluster_parameter_group),
    CacheSubnetGroupName=Ref(cache_cluster_subnet_group),
    ClusterName='nyctrees',
    Engine='redis',
    EngineVersion='2.8.6',
    NotificationTopicArn=Ref(notification_arn_param),
    NumCacheNodes=1,
    PreferredMaintenanceWindow='mon:01:30-mon:02:30',  # 9:30PM-10:30PM ET
    VpcSecurityGroupIds=[Ref(cache_cluster_security_group)]
))

#
# Route53 Resources
#
public_dns_records_sets = t.add_resource(r53.RecordSetGroup(
    'dnsPublicRecords',
    HostedZoneName=Join('', [Ref(hosted_zone_name_param), '.']),
    RecordSets=[
        r53.RecordSet(
            'dnsMonitoringServer',
            Name=Join('', ['monitoring.', Ref(hosted_zone_name_param), '.']),
            Type='A',
            TTL='300',
            ResourceRecords=[GetAtt(bastion_host, 'PublicIp')]
        )
    ]
))

private_dns_records_sets = t.add_resource(r53.RecordSetGroup(
    'dnsPrivateRecords',
    HostedZoneName='nyc-trees.internal.',
    RecordSets=[
        r53.RecordSet(
            'dnsBastionHost',
            Name='monitoring.service.nyc-trees.internal.',
            Type='A',
            TTL='10',
            ResourceRecords=[GetAtt(bastion_host, 'PrivateIp')]
        ),
        r53.RecordSet(
            'dnsDatabaseServer',
            Name='database.service.nyc-trees.internal.',
            Type='CNAME',
            TTL='10',
            ResourceRecords=[
                GetAtt(database_server_instance, 'Endpoint.Address')
            ]
        ),
        r53.RecordSet(
            'dnsCacheCluster',
            Name='cache.service.nyc-trees.internal.',
            Type='CNAME',
            TTL='10',
            # Create dummy record
            ResourceRecords=[Ref(cache_cluster_endpoint_param)]
        )
    ]
))

if __name__ == '__main__':
    utils.validate_cloudformation_template(t.to_json())

    file_name = __file__.replace('.py', '.json')

    with open(file_name, 'w') as f:
        f.write(t.to_json())

    print('Template validated and written to %s' % file_name)
