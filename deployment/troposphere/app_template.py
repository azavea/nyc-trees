from troposphere import Template, Parameter, Ref, Tags, Output, GetAtt, ec2

import template_utils as utils
import troposphere.autoscaling as asg
import troposphere.cloudwatch as cw
import troposphere.elasticloadbalancing as elb

t = Template()

t.add_version('2010-09-09')
t.add_description('An application server stack for the nyc-trees project.')

#
# Parameters
#
color_param = t.add_parameter(Parameter(
    'StackColor', Type='String',
    Description='Stack color', AllowedValues=['Blue', 'Green'],
    ConstraintDescription='must be either Blue or Green'
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

app_ssl_certificate_arm_param = t.add_parameter(Parameter(
    'AppSSLCertificateARN', Type='String',
    Description='Physical resource ID on an AWS::IAM::ServerCertificate for '
                'the application server load balancer'
))

app_server_ami_param = t.add_parameter(Parameter(
    'AppServerAMI', Type='String', Default='ami-d87dc6b0',
    Description='Application server AMI'
))

app_server_instance_profile_param = t.add_parameter(Parameter(
    'AppServerInstanceProfile', Type='String',
    Default='SendEmail',
    Description='Physical resource ID of an AWS::IAM::Role for the '
                'application servers'
))

app_server_instance_type_param = t.add_parameter(Parameter(
    'AppServerInstanceType', Type='String', Default='t2.micro',
    Description='Application server EC2 instance type',
    AllowedValues=utils.EC2_INSTANCE_TYPES,
    ConstraintDescription='must be a valid EC2 instance type.'
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
app_server_load_balancer_security_group = t.add_resource(ec2.SecurityGroup(
    'sgAppServerLoadBalancer',
    GroupDescription='Enables access to app servers via a load balancer',
    VpcId=Ref(vpc_param),
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', CidrIp=utils.ALLOW_ALL_CIDR, FromPort=p, ToPort=p
        )
        for p in [80, 443]
    ],
    SecurityGroupEgress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', CidrIp=utils.VPC_CIDR, FromPort=p, ToPort=p
        )
        for p in [80, 443]
    ],
    Tags=Tags(
        Name='sgAppServerLoadBalancer',
        Color=Ref(color_param)
    )
))

app_server_security_group = t.add_resource(ec2.SecurityGroup(
    'sgAppServer', GroupDescription='Enables access to application servers',
    VpcId=Ref(vpc_param),
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp', CidrIp=utils.VPC_CIDR, FromPort=p, ToPort=p
        )
        for p in [22, 80]
    ] + [
        ec2.SecurityGroupRule(
            IpProtocol='tcp', SourceSecurityGroupId=Ref(sg),
            FromPort=80, ToPort=80
        )
        for sg in [app_server_load_balancer_security_group]
    ],
    SecurityGroupEgress=[
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
    ],
    Tags=Tags(
        Name='sgAppServer',
        Color=Ref(color_param)
    )
))

#
# ELB Resources
#
app_server_load_balancer = t.add_resource(elb.LoadBalancer(
    'elbAppServer',
    # TODO: Create an S3 bucket automatically and enable logging.
    ConnectionDrainingPolicy=elb.ConnectionDrainingPolicy(
        Enabled=True,
        Timeout=300,
    ),
    CrossZone=True,
    SecurityGroups=[Ref(app_server_load_balancer_security_group)],
    Listeners=[
        elb.Listener(
            LoadBalancerPort='80',
            InstancePort='80',
            Protocol='HTTP',
        ),
        elb.Listener(
            LoadBalancerPort='443',
            InstancePort='80',
            Protocol='HTTPS',
            SSLCertificateId=Ref(app_ssl_certificate_arm_param)
        )
    ],
    HealthCheck=elb.HealthCheck(
        Target="HTTP:80/health-check/",
        HealthyThreshold="3",
        UnhealthyThreshold="2",
        Interval="30",
        Timeout="5",
    ),
    Subnets=Ref(public_subnets_param),
    Tags=Tags(
        Name='elbAppServer',
        Color=Ref(color_param)
    )
))

t.add_resource(cw.Alarm(
    'alarmAppServerBackend4XX',
    AlarmDescription='Application server backend 4XXs',
    AlarmActions=[Ref(notification_arn_param)],
    Statistic='Sum',
    Period=300,
    Threshold=5,
    EvaluationPeriods=1,
    ComparisonOperator='GreaterThanThreshold',
    MetricName='HTTPCode_Backend_4XX',
    Namespace='AWS/ELB',
    Dimensions=[
        cw.MetricDimension(
            'metricLoadBalancerName',
            Name='LoadBalancerName',
            Value=Ref(app_server_load_balancer)
        )
    ],
))

t.add_resource(cw.Alarm(
    'alarmAppServerBackend5XX',
    AlarmDescription='Application server backend 5XXs',
    AlarmActions=[Ref(notification_arn_param)],
    Statistic='Sum',
    Period=60,
    Threshold=0,
    EvaluationPeriods=1,
    ComparisonOperator='GreaterThanThreshold',
    MetricName='HTTPCode_Backend_5XX',
    Namespace='AWS/ELB',
    Dimensions=[
        cw.MetricDimension(
            'metricLoadBalancerName',
            Name='LoadBalancerName',
            Value=Ref(app_server_load_balancer)
        )
    ],
))

#
# Auto Scaling Group Resources
#
app_server_launch_config = t.add_resource(asg.LaunchConfiguration(
    'lcAppServer',
    ImageId=Ref(app_server_ami_param),
    IamInstanceProfile=Ref(app_server_instance_profile_param),
    InstanceType=Ref(app_server_instance_type_param),
    KeyName=Ref(keyname_param),
    SecurityGroups=[Ref(app_server_security_group)]
))

app_server_auto_scaling_group = t.add_resource(asg.AutoScalingGroup(
    'asgAppServer',
    AvailabilityZones=map(lambda x: 'us-east-1%s' % x,
                          utils.EC2_AVAILABILITY_ZONES),
    Cooldown=300,
    DesiredCapacity=2,
    HealthCheckGracePeriod=600,
    HealthCheckType='ELB',
    LaunchConfigurationName=Ref(app_server_launch_config),
    LoadBalancerNames=[Ref(app_server_load_balancer)],
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
    VPCZoneIdentifier=Ref(private_subnets_param),
    Tags=[
        asg.Tag('Name', 'AppServer', True),
        asg.Tag('Color', Ref(color_param), True)
    ]
))

#
# Outputs
#
t.add_output([
    Output(
        'AppServerLoadBalancerEndpoint',
        Description='Application server endpoint',
        Value=GetAtt(app_server_load_balancer, 'DNSName')
    ),
    Output(
        'AppServerLoadBalancerHostedZoneNameID',
        Description='ID of canonical hosted zone name for ELB',
        Value=GetAtt(
            app_server_load_balancer,
            'CanonicalHostedZoneNameID'
        )
    )
])

if __name__ == '__main__':
    utils.validate_cloudformation_template(t.to_json())

    file_name = __file__.replace('.py', '.json')

    with open(file_name, 'w') as f:
        f.write(t.to_json())

    print('Template validated and written to %s' % file_name)
