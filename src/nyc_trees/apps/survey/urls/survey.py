# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from apps.survey.routes import (survey, survey_from_event,
                                flag_survey, survey_detail,
                                confirm_survey, complete_survey)


# These URLs have the prefix 'survey/'
urlpatterns = patterns(
    '',
    url(r'^$', survey, name='survey'),

    url(r'^confirm/(?P<survey_id>\d+)/$',
        confirm_survey, name='confirm_survey'),

    url(r'^detail/(?P<survey_id>\d+)/$', survey_detail, name='survey_detail'),

    url(r'^(?P<group_slug>[\w-]+)/event/(?P<event_slug>[\w-]+)/$',
        survey_from_event, name='survey_from_event'),

    url(r'^flag/(?P<survey_id>\d+)/$', flag_survey, name='flag_survey'),

    url(r'^complete/(?P<survey_id>\d+)/$',
        complete_survey, name='complete_survey'),
)
