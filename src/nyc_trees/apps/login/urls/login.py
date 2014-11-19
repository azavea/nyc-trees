# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from django_tinsel.decorators import route

from apps.login.views import forgot_username_page_view, forgot_username_view


# Everything is mounted on login/
urlpatterns = patterns(
    '',
    url(r'^forgot-username/$',
        route(GET=forgot_username_page_view,
              POST=forgot_username_view),
        name='forgot_username'),
)
