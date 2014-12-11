from troposphere import Template, Parameter, Ref, Tags, Output, Join, GetAtt

import template_utils as utils
import troposphere.rds as rds
import troposphere.elasticache as ec

t = Template()

t.add_version('2010-09-09')
t.add_description('A data store server stack for the nyc-trees project.')

#
# Parameters
#
keyname_param = t.add_parameter(Parameter(
    'KeyName', Type='String', Default='nyc-trees-test',
    Description='Name of an existing EC2 key pair'
))

notification_arn_param = t.add_parameter(Parameter(
    'GlobalNotificationsARN', Type='String',
    Description='Physical resource ID of an AWS::SNS::Topic for notifications'
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

database_server_security_group = t.add_parameter(Parameter(
    'sgDatabaseServer', Type='String',
    Description='Physical resource ID of an AWS::EC2::SecurityGroup'
))

cache_cluster_security_group = t.add_parameter(Parameter(
    'sgCacheCluster', Type='String',
    Description='Physical resource ID of an AWS::EC2::SecurityGroup'
))

#
# Security Group Resources
#
bastion_security_group = t.add_resource(ec2.SecurityGroup(
    'sgBastion', GroupDescription='Enables access to the BastionHost',
    VpcId=Ref(vpc_param),
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(IpProtocol='tcp', CidrIp=Ref(office_cidr_param),
                              FromPort=p, ToPort=p)
        for p in [22, 5601, 8080]
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
# Resources
#
database_server_subnet_group = t.add_resource(rds.DBSubnetGroup(
    "dbsngDatabaseServer",
    DBSubnetGroupDescription='Private subnets for the RDS instances',
    SubnetIds=Ref(data_store_server_subnets_param),
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

cache_cluster_subnet_group = t.add_resource(ec.SubnetGroup(
    "ecsngCacheCluster",
    Description='Private subnets for the ElastiCache instances',
    SubnetIds=Ref(data_store_server_subnets_param)
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
# Outputs
#
t.add_output([
    Output(
        'DatabaseServerEndpoint',
        Description='Database server endpoint',
        Value=Join(':', [
            GetAtt('DatabaseServer', 'Endpoint.Address'),
            GetAtt('DatabaseServer', 'Endpoint.Port')
        ])
    ),
    # CacheCluster endpoint output is not supported for Redis. :(
])

if __name__ == '__main__':
    utils.validate_cloudformation_template(t.to_json())

    file_name = __file__.replace('.py', '.json')

    with open(file_name, 'w') as f:
        f.write(t.to_json())

    print('Template validated and written to %s' % file_name)
