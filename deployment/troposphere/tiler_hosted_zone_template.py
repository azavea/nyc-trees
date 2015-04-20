from troposphere import Template, Parameter, Ref, GetAtt, Join

import template_utils as utils
import troposphere.route53 as r53
import troposphere.cloudfront as cf

t = Template()

t.add_version('2010-09-09')
t.add_description('Tiler hosted zone records for the nyc-trees project.')

#
# Parameters
#
hosted_zone_name_param = t.add_parameter(Parameter(
    'PublicHostedZone', Type='String',
    Default='treescount.azavea.com',
    Description='Hosted zone name for public DNS'
))

tile_server_hosted_zone_alias_target_param = t.add_parameter(Parameter(
    'TileServerAliasTarget', Type='String',
    Description='Alias target for the hosted zone record set'
))

tile_server_load_balancer_hosted_zone_id_param = t.add_parameter(
    Parameter(
        'TileServerLoadBalancerHostedZoneNameID', Type='String',
        Description='ID of canonical hosted zone name for ELB'
    )
)

private_hosted_zone_id_param = t.add_parameter(Parameter(
    'PrivateHostedZoneId', Type='String',
    Description='Hosted zone ID for private record set'
))

#
# Public Route53 Resources
#
public_dns_records_sets = t.add_resource(r53.RecordSetGroup(
    'dnsPublicRecords',
    HostedZoneName=Join('', [Ref(hosted_zone_name_param), '.']),
    RecordSets=[
        r53.RecordSet(
            'dnsTileServers',
            AliasTarget=r53.AliasTarget(
                Ref(tile_server_load_balancer_hosted_zone_id_param),
                Join(
                    '',
                    [Ref(tile_server_hosted_zone_alias_target_param), '.']
                ),
                True
            ),
            Name=Join('', ['tiles.', Ref(hosted_zone_name_param), '.']),
            Type='A'
        )
    ]
))

#
# CloudFront Resources
#
cloudfront_tile_distribution = t.add_resource(cf.Distribution(
    'tileDistribution',
    DistributionConfig=cf.DistributionConfig(
        Origins=[
            cf.Origin(
                Id='tileOriginId',
                DomainName=Join('.', ['tiles', Ref(hosted_zone_name_param)]),
                CustomOriginConfig=cf.CustomOrigin(
                    OriginProtocolPolicy='http-only'
                )
            )
        ],
        DefaultCacheBehavior=cf.DefaultCacheBehavior(
            ForwardedValues=cf.ForwardedValues(QueryString=True),
            TargetOriginId='tileOriginId',
            ViewerProtocolPolicy='allow-all'
        ),
        Enabled=True
    )
))

#
# Private Route53 Resources
#
private_dns_records_sets = t.add_resource(r53.RecordSetGroup(
    'dnsPrivateRecords',
    HostedZoneId=Ref(private_hosted_zone_id_param),
    RecordSets=[
        r53.RecordSet(
            'dnsTileServers',
            Name='tile.service.nyc-trees.internal.',
            Type='CNAME',
            TTL='10',
            ResourceRecords=[
                GetAtt(cloudfront_tile_distribution, 'DomainName')
            ]
        )
    ]
))

if __name__ == '__main__':
    utils.validate_cloudformation_template(t.to_json())

    file_name = __file__.replace('.py', '.json')

    with open(file_name, 'w') as f:
        f.write(t.to_json())

    print('Template validated and written to %s' % file_name)
