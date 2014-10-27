# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url
from apps.core.decorators import route
from apps.registration.views import (registration_page, register_user, registration_complete_page, activate_registration_page, activate_user, activation_complete_page, login_page, login_user, forgot_password_page, forgot_password, forgot_username_page, forgot_username, forgot_username_email_sent_page, forgot_password_email_sent_page)


urlpatterns = patterns(
    '',
    # https://github.com/macropin/django-registration/blob/master/registration/backends/default/urls.py
    # used as reference
    url(r'^register/$', route(GET=registration_page,
                              POST=register_user),
        name='register_user'),

    url(r'^register-complete/$',
        route(GET=registration_complete_page),
        name='registration_complete_page'),

    url(r'^activate/(?P<hash>[^/]+)/$',
        route(GET=activate_registration_page,
              POST=activate_user),
        name='activate_user'),

    url(r'^activate-complete/$',
        route(GET=activation_complete_page),
        name='activation_complete_page'),

    url(r'^login/$',
        route(GET=login_page,
              POST=login_user),
        name='login_user'),

    url(r'^login/forgot-password/$',
        route(GET=forgot_password_page,
              POST=forgot_password),
        name='forgot_password'),

    url(r'^login/forgot-username/$',
        route(GET=forgot_username_page,
              POST=forgot_username),
        name='forgot_username'),

    url(r'^login/forgot-username-complete/$',
        route(GET=forgot_username_email_sent_page),
        name='forgot_username_email_sent_page'),

    url(r'^login/forgot-password-complete/$',
        route(GET=forgot_password_email_sent_page),
        name='forgot_password_email_sent_page'),
)
