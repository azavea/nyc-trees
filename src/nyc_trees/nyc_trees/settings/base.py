"""Common settings and globals."""

from os import environ
from os.path import abspath, basename, dirname, join, normpath, exists
from sys import path
import json
from datetime import timedelta


# PATH CONFIGURATION
# Absolute filesystem path to the Django nyc_trees/nyc_trees directory:
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level nyc_trees/ folder:
SITE_ROOT = dirname(DJANGO_ROOT)

# Site name:
SITE_NAME = basename(DJANGO_ROOT)

SITE_ID = 1  # Needed by django.contrib.sites (used by Django flatpages)

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)
# END PATH CONFIGURATION


# DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
# END DEBUG CONFIGURATION


# STATSD CONFIGURATION
STATSD_CLIENT = 'django_statsd.clients.normal'
STATSD_PREFIX = 'django'
STATSD_HOST = environ.get('NYC_TREES_STATSD_HOST', 'localhost')
# END STATSD CONFIGURATION


# EMAIL CONFIGURATION
DEFAULT_FROM_EMAIL = 'noreply@treescount.nycgovparks.org'
DEFAULT_HELP_EMAIL = 'treescount.help@parks.nyc.gov'
# END EMAIL CONFIGURATION


# FILE STORAGE CONFIGURATION
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
# END FILE STORAGE CONFIGURATION


# CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        # The Redis database at index 0 is used by Logstash/Beaver
        'LOCATION': 'redis://{0}:{1}/1'.format(
            environ.get('NYC_TREES_CACHE_HOST', 'localhost'),
            environ.get('NYC_TREES_CACHE_PORT', 6379)),
        'OPTIONS': {
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'SOCKET_TIMEOUT': 3,
        }
    }
}

# Don't throw exceptions if Redis is down.
DJANGO_REDIS_IGNORE_EXCEPTIONS = True
# END CACHE CONFIGURATION


# CELERY CONFIGURATION
BROKER_URL = 'redis://{0}:{1}/2'.format(
    environ.get('NYC_TREES_CACHE_HOST', 'localhost'),
    environ.get('NYC_TREES_CACHE_PORT', 6379))

CELERY_RESULT_BACKEND = BROKER_URL

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

STATSD_CELERY_SIGNALS = True
# END CELERY CONFIGURATION


# DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': environ.get('NYC_TREES_DB_NAME', 'nyc_trees'),
        'USER': environ.get('NYC_TREES_DB_USER', 'nyc_trees'),
        'PASSWORD': environ.get('NYC_TREES_DB_PASSWORD', 'nyc_trees'),
        'HOST': environ.get('NYC_TREES_DB_HOST', 'localhost'),
        'PORT': environ.get('NYC_TREES_DB_PORT', 5432),
        'TEST_NAME': environ.get('NYC_TREES_TEST_DB_NAME', 'test_nyc_trees')
    }
}

POSTGIS_VERSION = tuple(
    map(int, environ.get('DJANGO_POSTGIS_VERSION', '2.1.3').split("."))
)
# END DATABASE CONFIGURATION


# LOGGING CONFIGURATION
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }
}
# END LOGGING CONFIGURATION


# GENERAL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
TIME_ZONE = 'America/New_York'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = False

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = False

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# This generates false positives and is being removed
# (https://code.djangoproject.com/ticket/23469)
SILENCED_SYSTEM_CHECKS = ['1_6.W001', '1_6.W002']
# END GENERAL CONFIGURATION


# MEDIA CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = environ['DJANGO_MEDIA_ROOT']

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'
# END MEDIA CONFIGURATION


# STATIC FILE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = environ['DJANGO_STATIC_ROOT']

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS  # NOQA
STATICFILES_DIR = '/var/cache/nyc-trees/static/'
STATICFILES_DIRS = (
    STATICFILES_DIR,
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders  # NOQA
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# parse manifest created by gulp-rev-all
_STATIC_FILES_MAP = join(STATICFILES_DIR, 'rev-manifest.json')
if exists(_STATIC_FILES_MAP):
    with open(_STATIC_FILES_MAP) as json_file:
        STATIC_FILES_MAPPING = json.load(json_file)
else:
    STATIC_FILES_MAPPING = {}
# END STATIC FILE CONFIGURATION


# SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key should only be used for development and testing.
SECRET_KEY = r"nyixt#@$+hra95q3_x96#erfzf0@*fc&q!u!aqs*xlls3ddd!w"
# END SECRET CONFIGURATION


# SITE CONFIGURATION
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []
# END SITE CONFIGURATION


# FIXTURE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS  # NOQA
FIXTURE_DIRS = (
    normpath(join(SITE_ROOT, 'fixtures')),
)
# END FIXTURE CONFIGURATION


# TEMPLATE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors  # NOQA
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'nyc_trees.context_processors.user_settings_privacy_url',
    'nyc_trees.context_processors.config',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
TEMPLATE_DIRS = (
    normpath(join(SITE_ROOT, 'templates')),
)
# END TEMPLATE CONFIGURATION


# MIDDLEWARE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
MIDDLEWARE_CLASSES = (
    # Default Django middleware.
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_statsd.middleware.GraphiteRequestTimingMiddleware',
    'django_statsd.middleware.GraphiteMiddleware',
    'waffle.middleware.WaffleMiddleware',
    'nyc_trees.middleware.SoftLaunchMiddleware',
)
# END MIDDLEWARE CONFIGURATION


# URL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = '%s.urls' % SITE_NAME
# END URL CONFIGURATION


AUTH_USER_MODEL = 'core.User'


# APP CONFIGURATION
DJANGO_APPS = (
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.flatpages',
    'django.contrib.gis',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.admin',
)

THIRD_PARTY_APPS = (
    'registration',
    'django_statsd',
    'floppyforms',
    'widget_tweaks',
    'waffle',
    'watchman',
)

# THIRD-PARTY CONFIGURATION

# django-registration-redux
ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_AUTO_LOGIN = True

# django-watchman
# Disable Storage checking, to avoid creating files on S3 on every health check
WATCHMAN_CHECKS = (
    'watchman.checks.caches',
    'watchman.checks.databases',
)

# END THIRD-PARTY CONFIGURATION

# Apps specific for this project go here.
LOCAL_APPS = (
    'apps.core',
    'apps.census_admin',
    'apps.event',
    'apps.home',
    'apps.login',
    'apps.survey',
    'apps.users',
    'apps.geocode',
    'apps.mail'
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
# END APP CONFIGURATION


# WSGI CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = '%s.wsgi.application' % SITE_NAME
# END WSGI CONFIGURATION

LOGIN_REDIRECT_URL = 'user_detail_redirect'

OMGEO_SETTINGS = [[
    'omgeo.services.EsriWGS', {}
]]

# New York City bounds from http://www.mapdevelopers.com/geocode_bounding_box.php  # NOQA
NYC_BOUNDS = (-74.259088, 40.495996, -73.700272, 40.915256)

# If geocoding a string produces no results, this string will be
# appended for a second attempt.
GEOCODE_FALLBACK_SUFFIX = ', New York, NY'

# The maximum number of blockface reservations per user
RESERVATIONS_LIMIT = 12

# How long blockface reservations will last
RESERVATION_TIME_PERIOD = timedelta(days=7)

TILER_URL = '//%s' % environ.get('TILER_HOST', 'localhost')

MAX_GROUP_IMAGE_SIZE_IN_BYTES = 102400  # 100 KB

SOFT_LAUNCH_REDIRECT_URL = "/"
SOFT_LAUNCH_REGEXES = [
    r'^/user/',
    r'^/accounts/',
    r'^/login/',
    r'^/faq/',
    r'^/admin/',
    r'^/health-check/',
]

RESERVATION_REMINDER_WINDOW = 3

ADMIN_OPENLAYERS_URL = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/'\
                       '2.13.1/OpenLayers.js'
