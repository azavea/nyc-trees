from troposphere import Template, Parameter, Ref
from os.path import basename

import template_utils as utils
import troposphere.autoscaling as asg

t = Template()

t.add_version('2010-09-09')
t.add_description('A tiler stack for the nyc-trees project.')

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

tile_server_ami_param = t.add_parameter(Parameter(
    'TileServerAMI', Type='String', Default='ami-d87dc6b0',
    Description='Tile server AMI'
))

tile_server_instance_profile_param = t.add_parameter(Parameter(
    'TileServerInstanceProfile', Type='String',
    Default=
    'arn:aws:iam::900325299081:instance-profile/TileServerInstanceProfile',
    Description='Physical resource ID of an AWS::IAM::Role for the '
                'tile servers'
))

tile_server_instance_type_param = t.add_parameter(Parameter(
    'TileServerInstanceType', Type='String', Default='t2.micro',
    Description='Tile server EC2 instance type',
    AllowedValues=utils.EC2_INSTANCE_TYPES,
    ConstraintDescription='must be a valid EC2 instance type.'
))

tile_server_load_balancer = t.add_parameter(Parameter(
    'elbTileServer', Type='String',
    Description='Name of an AWS::ElasticLoadBalancing::LoadBalancer'
))

tile_server_security_group = t.add_parameter(Parameter(
    'sgTileServer', Type='String',
    Description='Physical resource ID of an AWS::EC2::SecurityGroup'
))

tile_server_subnets_param = t.add_parameter(Parameter(
    'TileServerSubnets', Type='CommaDelimitedList',
    Description='A list of subnets to associate with the tile server '
                'load balancer'
))

#
# Resources
#
tile_server_launch_config = t.add_resource(asg.LaunchConfiguration(
    'lcTileServer',
    ImageId=Ref(tile_server_ami_param),
    IamInstanceProfile=Ref(tile_server_instance_profile_param),
    InstanceType=Ref(tile_server_instance_type_param),
    KeyName=Ref(keyname_param),
    SecurityGroups=[Ref(tile_server_security_group)]
))

tile_server_auto_scaling_group = t.add_resource(asg.AutoScalingGroup(
    'asgTileServer',
    AvailabilityZones=map(lambda x: 'us-east-1%s' % x,
                          utils.EC2_AVAILABILITY_ZONES),
    Cooldown=300,
    DesiredCapacity=2,
    HealthCheckGracePeriod=600,
    HealthCheckType='ELB',
    LaunchConfigurationName=Ref(tile_server_launch_config),
    LoadBalancerNames=[Ref(tile_server_load_balancer)],
    MaxSize=2,
    MinSize=2,
    NotificationConfiguration=asg.NotificationConfiguration(
        TopicARN=Ref(notification_arn_param),
        NotificationTypes=[
            asg.EC2_INSTANCE_LAUNCH,
            asg.EC2_INSTANCE_LAUNCH_ERROR,
            asg.EC2_INSTANCE_TERMINATE,
            asg.EC2_INSTANCE_TERMINATE_ERROR
        ]
    ),
    VPCZoneIdentifier=Ref(tile_server_subnets_param),
    Tags=[asg.Tag('Name', 'TileServer', True)]
))

if __name__ == '__main__':
    utils.validate_cloudformation_template(t.to_json())

    file_name = basename(__file__).replace('.py', '.json')

    with open(file_name, 'w') as f:
        f.write(t.to_json())

    print('Template validated and written to %s' % file_name)
