# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from apps.login import routes as r


# Everything is mounted on login/
urlpatterns = patterns(
    '',
    url(r'^forgot-username/$',
        r.forgot_username,
        name='forgot_username'),
)
