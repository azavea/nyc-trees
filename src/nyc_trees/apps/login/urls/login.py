# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from apps.login import routes as r


# Everything is mounted on accounts/
urlpatterns = patterns(
    '',
    url(r'^forgot-username/$',
        r.forgot_username,
        name='forgot_username'),

    url(r'^forgot-username/sent/$',
        r.forgot_username_sent,
        name='forgot_username_sent'),

    url(r'^password-reset-activation-email/$',
        r.password_reset_resend_activation,
        name='password_reset_resend_activation'),

    url(r'^send-activation-email/$',
        r.send_activation_email,
        name='send_activation_email'),

    url(r'^send-activation-email/sent/$',
        r.activation_email_sent,
        name='activation_email_sent'),

    url(r'^send-activation-email/activated/$',
        r.activated,
        name='activated')
)
