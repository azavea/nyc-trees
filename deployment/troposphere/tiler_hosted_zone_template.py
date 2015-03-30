from troposphere import Template, Parameter, Ref, GetAtt

import template_utils as utils
import troposphere.route53 as r53
import troposphere.cloudfront as cf

t = Template()

t.add_version('2010-09-09')
t.add_description('Tiler hosted zone records for the nyc-trees project.')

#
# Parameters
#
tile_server_hosted_zone_alias_target_param = t.add_parameter(Parameter(
    'TileServerAliasTarget', Type='String',
    Description='Alias target for the hosted zone record set'
))

private_hosted_zone_id_param = t.add_parameter(Parameter(
    'PrivateHostedZoneId', Type='String',
    Description='Hosted zone ID for private record set'
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
                DomainName=Ref(tile_server_hosted_zone_alias_target_param),
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
# Route53 Resources
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
