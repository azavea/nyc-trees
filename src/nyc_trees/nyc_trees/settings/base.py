"""Common settings and globals."""

from os import environ
from os.path import abspath, basename, dirname, join, normpath, exists
from sys import path
import json


# PATH CONFIGURATION
# Absolute filesystem path to the Django nyc_trees/nyc_trees directory:
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level nyc_trees/ folder:
SITE_ROOT = dirname(DJANGO_ROOT)


# Site name:
SITE_NAME = basename(DJANGO_ROOT)

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
STATSD_HOST = environ.get('NYC_TREES_STATSD_HOST', 'localhost')
# END STATSD CONFIGURATION


# DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': environ.get('NYC_TREES_DB_NAME', 'nyc_trees'),
        'USER': environ.get('NYC_TREES_DB_USER', 'nyc_trees'),
        'PASSWORD': environ.get('NYC_TREES_DB_PASSWORD', 'nyc_trees'),
        'HOST': environ.get('NYC_TREES_DB_HOST', 'localhost'),
        'PORT': environ.get('NYC_TREES_DB_PORT', 5432)
    }
}

POSTGIS_VERSION = tuple(
    map(int, environ.get('DJANGO_POSTGIS_VERSION', '2.1.6').split("."))
)
# END DATABASE CONFIGURATION


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
SILENCED_SYSTEM_CHECKS = ['1_6.W001']
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
    'django.contrib.gis',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Useful template tags:
    # 'django.contrib.humanize',

    'django.contrib.admin',
)

THIRD_PARTY_APPS = (
    'registration',
    'django_statsd',
    'floppyforms',
)

# THIRD-PARTY CONFIGURATION

# django-registration-redux
ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_AUTO_LOGIN = True

# END THIRD-PARTY CONFIGURATION

# Apps specific for this project go here.
LOCAL_APPS = (
    'apps.core',
    'apps.quiz',
    'apps.census_admin',
    'apps.event',
    'apps.home',
    'apps.login',
    'apps.survey',
    'apps.users',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
# END APP CONFIGURATION


# LOGGING CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# TODO: Use logstash for logging
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': [],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
# END LOGGING CONFIGURATION


# WSGI CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = '%s.wsgi.application' % SITE_NAME
# END WSGI CONFIGURATION

LOGIN_REDIRECT_URL = 'user_detail_redirect'
