# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url, include

from apps.login import routes as r


urlpatterns = patterns(
    '',
    url(r'^logout/$', r.logout, name='logout'),
    # /accounts/password/reset/ is purposefully shadowing an endpoint and must
    # come before the registration and auth urls are imported
    url(r'^password/reset/$', r.password_reset, name='password_reset'),
    # TODO: resolve this duplicate mapping Both
    # /accounts/password/reset/ and /accounts/password_reset/ are
    # mapped to views via library code. We need to find a long term
    # solution to this ambiguity but for now I am ensuring that both
    # password reset URLs are mapped to the customized view.
    url(r'^password_reset/$', r.password_reset, name='password_reset_alt'),

    # Shadows django-registration-redux endpoint.
    # Ref: https://github.com/macropin/django-registration/blob/master/registration/backends/default/urls.py # NOQA
    url(r'^activate/complete/$', r.activation_complete,
        name='registration_activation_complete'),

    # Shadows django-registration-redux endpoint.
    # Ref: https://github.com/macropin/django-registration/blob/master/registration/backends/default/urls.py # NOQA
    url(r'^register/$', r.register, name='registration_register'),

    url(r'^', include('registration.backends.default.urls')),
    url(r'^', include('django.contrib.auth.urls')),
)
