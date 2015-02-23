# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from apps.survey.routes import survey, survey_from_event


# These URLs have the prefix 'survey/'
urlpatterns = patterns(
    '',
    url(r'^$', survey, name='survey'),

    url(r'^(?P<group_slug>[\w-]+)/event/(?P<event_slug>[\w-]+)/',
        survey_from_event, name='survey_from_event'),
)
