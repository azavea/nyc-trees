# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url, include

from apps.login.backends import NycRegistrationView
from apps.login.views import password_reset

urlpatterns = patterns(
    '',
    # /accounts/password/reset/ is purposefully shadowing an endpoint and must
    # come before the registration and auth urls are imported
    url(r'^password/reset/$', password_reset, name='password_reset'),
    # TODO: resolve this duplicate mapping Both
    # /accounts/password/reset/ and /accounts/password_reset/ are
    # mapped to views via library code. We need to find a long term
    # solution to this ambiguity but for now I am ensuring that both
    # password reset URLs are mapped to the customized view.
    url(r'^password_reset/$', password_reset, name='password_reset_alt'),
    # accounts/register/ is purposefully shadowing an endpoint in the default
    # registration backend.  It must come before it
    url(r'^register/$',
        NycRegistrationView.as_view(),
        name='registration_register'),
    url(r'^', include('registration.backends.default.urls')),
    url(r'^', include('django.contrib.auth.urls')),
)
