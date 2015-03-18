"""Production settings and globals."""


from os import environ
from dns import resolver, exception
from boto.utils import get_instance_metadata

from base import *  # NOQA

# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured


def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return environ[setting]
    except KeyError:
        error_msg = "Set the %s env variable" % setting
        raise ImproperlyConfigured(error_msg)


instance_metadata = get_instance_metadata(timeout=5)

if not instance_metadata:
    raise ImproperlyConfigured('Unable to access the instance metadata')


# HOST CONFIGURATION
# See: https://docs.djangoproject.com/en/1.5/releases/1.5/#allowed-hosts-required-in-production  # NOQA
ALLOWED_HOSTS = [
    'treescount.nycgovparks.org',
    'treescount.azavea.com',
    '.elb.amazonaws.com',
    'localhost'
]

# ELBs use the instance IP in the Host header and ALLOWED_HOSTS checks against
# the Host header.
ALLOWED_HOSTS.append(instance_metadata['local-ipv4'])
# END HOST CONFIGURATION

# EMAIL CONFIGURATION
EMAIL_BACKEND = 'apps.core.mail.backends.boto.EmailBackend'
EMAIL_BOTO_CHECK_QUOTA = False
# END EMAIL CONFIGURATION


# SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = get_env_setting('DJANGO_SECRET_KEY')
# END SECRET CONFIGURATION

# TILER CONFIGURATION
try:
    import logging

    logger = logging.getLogger(__name__)

    # Lookup the CNAME record for TILER_HOST. Should be
    # tile.service.nyc-trees.internal and resolve to the CloudFront
    # distribution FQDN.
    answers = resolver.query(environ.get('TILER_HOST'), 'CNAME')

    if answers:
        # Remove trailing period because that's part of the DNS specification.
        TILER_URL = '//%s' % (str(answers[0]).rstrip('.'))
    else:
        logger.debug('TILER_HOST DNS query returned no answers')
except exception.DNSException:
    logger.exception('Failed to resolve TILER_HOST, %s' %
                     environ.get('TILER_HOST'))
# END TILER CONFIGURATION

# Django Storages CONFIGURATION
mac_metadata = instance_metadata['network']['interfaces']['macs']
vpc_id = mac_metadata.values()[0]['vpc-id']

# The VPC id should stay the same for all app servers in a particular
# environment and remain the same after a new deploy, but differ between
# environments.  This makes it a suitable S3 bucket name
AWS_STORAGE_BUCKET_NAME = 'django-storages-{}'.format(vpc_id)

AWS_AUTO_CREATE_BUCKET = True
DEFAULT_FILE_STORAGE = 'libs.custom_storages.PublicS3BotoStorage'

# There is no need to specify access key or secret key
# They are pulled from the instance metadata by Boto

# END Django Storages CONFIGURATION
