from troposphere import Template, Parameter, Ref, Join

import template_utils as utils
import troposphere.route53 as r53

t = Template()

t.add_version('2010-09-09')
t.add_description('A VPC stack for the nyc-trees project.')

#
# Parameters
#
hosted_zone_param = t.add_parameter(Parameter(
    'HostedZone', Type='String', Default='nyc-trees.internal',
    Description="The DNS name of an existing Amazon Route 53 hosted zone"
))

bastion_host_private_ip_param = t.add_parameter(Parameter(
    'BastionPrivateIPAddress', Type='String',
    Description='Private IP address of the BastionHost'
))

database_server_endpoint_param = t.add_parameter(Parameter(
    'DatabaseServerEndpoint', Type='String',
    Description='Database server endpoint'
))

cache_cluster_endpoint_param = t.add_parameter(Parameter(
    'CacheClusterEndpoint', Type='String',
    Description='Cache cluster endpoint'
))

tile_server_load_balancer_endpoint = t.add_parameter(Parameter(
    'TileServerLoadBalancerEndpoint', Type='String',
    Description='Tile server endpoint'
))

#
# Route53 Resources
#
private_dns_records_sets = t.add_resource(r53.RecordSetGroup(
    'dnsPrivateRecords',
    HostedZoneName=Join('', [Ref(hosted_zone_param), '.']),
    RecordSets=[
        r53.RecordSet(
            'dnsBastionHost',
            Name=Join("",
                      ['monitoring.service.', Ref(hosted_zone_param), '.']),
            Type='A',
            TTL='60',
            ResourceRecords=[Ref(bastion_host_private_ip_param)]
        ),
        r53.RecordSet(
            'dnsDatabaseServer',
            Name=Join("", ['database.service.', Ref(hosted_zone_param), '.']),
            Type='CNAME',
            TTL='60',
            ResourceRecords=[Ref(database_server_endpoint_param)]
        ),
        r53.RecordSet(
            'dnsCacheCluster',
            Name=Join("", ['cache.service.', Ref(hosted_zone_param), '.']),
            Type='CNAME',
            TTL='60',
            ResourceRecords=[Ref(cache_cluster_endpoint_param)]
        ),
        r53.RecordSet(
            'dnsTileServers',
            Name=Join("", ['tile.service.', Ref(hosted_zone_param), '.']),
            Type='CNAME',
            TTL='60',
            ResourceRecords=[Ref(tile_server_load_balancer_endpoint)]
        )
    ]
))

if __name__ == '__main__':
    utils.validate_cloudformation_template(t.to_json())

    file_name = __file__.replace('.py', '.json')

    with open(file_name, 'w') as f:
        f.write(t.to_json())

    print('Template validated and written to %s' % file_name)
