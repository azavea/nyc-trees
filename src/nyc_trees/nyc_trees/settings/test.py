from base import *  # NOQA

# TEST SETTINGS
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

SELENIUM_DEFAULT_BROWSER = 'firefox'
SELENIUM_TEST_COMMAND_OPTIONS = {'pattern': 'uitest*.py'}

INSTALLED_APPS += ('sbo_selenium',)
