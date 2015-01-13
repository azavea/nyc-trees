import json
import base64
import hmac
import hashlib

from django.conf import settings
from django.core.mail.backends import smtp

from urllib2 import urlopen, URLError

SES_SMTP_CONVERSION_HMAC_MESSAGE = 'SendRawEmail'
SES_SMTP_CONVERSION_VERSION = '\x02'

_IAM_URL_TEMPLATE = ('http://instance-data.ec2.internal/latest/'
                     'meta-data/iam/security-credentials/%s')


def hash_smtp_pass_from_secret_key(key):
    h = hmac.new(key.encode('utf-8'),
                 SES_SMTP_CONVERSION_HMAC_MESSAGE,
                 digestmod=hashlib.sha256)
    return base64.b64encode("{0}{1}".format(SES_SMTP_CONVERSION_VERSION,
                                            h.digest()))


class IAMCredentialsBackend(smtp.EmailBackend):
    def __init__(self, *args, **kwargs):
        try:
            r = urlopen(_IAM_URL_TEMPLATE % settings.AWS_IAM_ROLE_NAME)
            payload = json.loads(r.read())
        except (URLError, ValueError):
            if kwargs.get('fail_silently'):
                payload = {'AccessKeyId': None,
                           'SecretAccessKey': None}
            else:
                raise

        iam_password = payload['SecretAccessKey'].encode('utf-8')
        ses_smtp_password = hash_smtp_pass_from_secret_key(iam_password)
        kwargs['password'] = ses_smtp_password
        kwargs['username'] = payload['AccessKeyId'].encode('utf-8')

        super(IAMCredentialsBackend, self).__init__(*args, **kwargs)
