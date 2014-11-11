# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url, include

from registration.backends.default.views import RegistrationView
from registration.forms import RegistrationFormUniqueEmail


urlpatterns = patterns(
    '',
    # accounts/register/ is purposefully shadowing an endpoint in the default
    # registration backend.  It must come before it
    url(r'^register/$',
        RegistrationView.as_view(form_class=RegistrationFormUniqueEmail),
        name='registration_register'),
    url(r'^', include('registration.backends.default.urls')),
    url(r'^', include('django.contrib.auth.urls')),
)
