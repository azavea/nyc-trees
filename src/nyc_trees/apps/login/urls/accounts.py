# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url, include

from apps.login.backends import NycRegistrationView

urlpatterns = patterns(
    '',
    # accounts/register/ is purposefully shadowing an endpoint in the default
    # registration backend.  It must come before it
    url(r'^register/$',
        NycRegistrationView.as_view(),
        name='registration_register'),
    url(r'^', include('registration.backends.default.urls')),
    url(r'^', include('django.contrib.auth.urls')),
)
