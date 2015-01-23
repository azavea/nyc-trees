# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from apps.quiz.routes import quiz_list_page, quiz_page


# These URLs have the prefix 'quiz/'
urlpatterns = patterns(
    '',

    url(r'^$', quiz_list_page, name='quiz_list_page'),

    url(r'^(?P<quiz_slug>[\w-]+)/$', quiz_page, name='quiz')
)
