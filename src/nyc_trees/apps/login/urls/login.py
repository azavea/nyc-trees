# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from django_tinsel.decorators import route

from apps.login.views import (
    forgot_username_page, forgot_username, forgot_username_email_sent_page
)


# Everything is mounted on login/
urlpatterns = patterns(
    '',
    url(r'^forgot-username/$',
        route(GET=forgot_username_page,
              POST=forgot_username),
        name='forgot_username'),

    url(r'^forgot-username-complete/$',
        route(GET=forgot_username_email_sent_page),
        name='forgot_username_email_sent_page'),
)
