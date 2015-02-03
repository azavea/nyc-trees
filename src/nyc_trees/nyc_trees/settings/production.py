"""Production settings and globals."""


from os import environ
from urllib2 import urlopen, URLError
from dns import resolver, exception

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
try:
    ALLOWED_HOSTS.append(
        urlopen(
            'http://instance-data.ec2.internal/latest/meta-data/local-ipv4'
        ).readline()
    )
except URLError:
    pass
# END HOST CONFIGURATION

# EMAIL CONFIGURATION
EMAIL_BACKEND = 'apps.core.mail.backends.boto.EmailBackend'
EMAIL_BOTO_CHECK_QUOTA = False
# END EMAIL CONFIGURATION


# CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
# END CACHE CONFIGURATION


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

SOFT_LAUNCH_ENABLED = False
