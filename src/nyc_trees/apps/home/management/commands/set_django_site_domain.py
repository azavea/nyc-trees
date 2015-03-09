from optparse import make_option

from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Used to set django_site domain and name'

    option_list = BaseCommand.option_list + (
        make_option('--django-site-name',
                    action='store',
                    dest='django_site_name',
                    default='treescount.nycgovparks.org',
                    help='Sets the default site name. Defaults to '
                         '"treescount.nycgovparks.org"'),
        make_option('--django-site-domain',
                    action='store',
                    dest='django_site_domain',
                    default='treescount.nycgovparks.org',
                    help='Sets the default site domain. Defaults to '
                         '"treescount.nycgovparks.org"'),
        )

    def handle(self, *args, **options):
        site = Site.objects.get_current()
        site.name = options.get('django_site_name')
        site.domain = options.get('django_site_domain')
        site.save()
