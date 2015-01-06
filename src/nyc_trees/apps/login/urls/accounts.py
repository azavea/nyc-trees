# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required

from django_tinsel.utils import decorate as do
from django_tinsel.decorators import route, render_template

from apps.login.backends import NycRegistrationView
from apps.login.views import (password_reset, logout,
                              activation_complete, save_optional_info)


urlpatterns = patterns(
    '',
    url(r'^logout/$', logout, name='logout'),
    # /accounts/password/reset/ is purposefully shadowing an endpoint and must
    # come before the registration and auth urls are imported
    url(r'^password/reset/$', password_reset, name='password_reset'),
    # TODO: resolve this duplicate mapping Both
    # /accounts/password/reset/ and /accounts/password_reset/ are
    # mapped to views via library code. We need to find a long term
    # solution to this ambiguity but for now I am ensuring that both
    # password reset URLs are mapped to the customized view.
    url(r'^password_reset/$', password_reset, name='password_reset_alt'),

    # Shadows django-registration-redux endpoint.
    # Ref: https://github.com/macropin/django-registration/blob/master/registration/backends/default/urls.py # NOQA
    url(r'^activate/complete/$',
        do(login_required,
           render_template('registration/activation_complete.html'),
           route(GET=activation_complete,
                 POST=save_optional_info)),
        name='registration_activation_complete'),

    # Shadows django-registration-redux endpoint.
    # Ref: https://github.com/macropin/django-registration/blob/master/registration/backends/default/urls.py # NOQA
    url(r'^register/$',
        NycRegistrationView.as_view(),
        name='registration_register'),

    url(r'^', include('registration.backends.default.urls')),
    url(r'^', include('django.contrib.auth.urls')),
)
