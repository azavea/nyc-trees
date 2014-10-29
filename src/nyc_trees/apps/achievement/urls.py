# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from apps.core.decorators import route, is_logged_in
from apps.achievement.views import quiz_list_page, quiz_page, complete_quiz


# These URLs have the prefix 'quiz/'
urlpatterns = patterns(
    '',
    url(r'^$',
        route(GET=quiz_list_page),
        name='quiz_list_page'),

    url(r'^(?P<quiz_id>\d+)/$',
        # We could maybe let people start, but not complete a quiz
        # when not loggged in
        is_logged_in(route(GET=quiz_page,
                        POST=complete_quiz)),
        name='quiz'),
    )
