from troposphere import Template, Parameter, Ref, Join

import template_utils as utils
import troposphere.route53 as r53

t = Template()

t.add_version('2010-09-09')
t.add_description('Application hosted zone records for the nyc-trees project.')

#
# Parameters
#
hosted_zone_name_param = t.add_parameter(Parameter(
    'PublicHostedZone', Type='String',
    Default='treescount.azavea.com',
    Description='Hosted zone name for public DNS'
))

app_server_hosted_zone_alias_target_param = t.add_parameter(Parameter(
    'AppServerAliasTarget', Type='String',
    Description='Alias target for the hosted zone record set'
))

app_server_load_balancer_hosted_zone_id_param = t.add_parameter(
    Parameter(
        'AppServerLoadBalancerHostedZoneNameID', Type='String',
        Description='ID of canonical hosted zone name for ELB'
    )
)

#
# Route53 Resources
#
public_dns_records_sets = t.add_resource(r53.RecordSetGroup(
    'dnsPublicRecords',
    HostedZoneName=Join('', [Ref(hosted_zone_name_param), '.']),
    RecordSets=[
        r53.RecordSet(
            'dnsAppServers',
            AliasTarget=r53.AliasTarget(
                Ref(app_server_load_balancer_hosted_zone_id_param),
                Join(
                    '',
                    [Ref(app_server_hosted_zone_alias_target_param), '.']
                )
            ),
            Name=Ref(hosted_zone_name_param),
            Type='A'
        )
    ]
))

if __name__ == '__main__':
    utils.validate_cloudformation_template(t.to_json())

    file_name = __file__.replace('.py', '.json')

    with open(file_name, 'w') as f:
        f.write(t.to_json())

    print('Template validated and written to %s' % file_name)
