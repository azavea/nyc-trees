# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url
from apps.users.routes import user as r

# These URLs have the prefix 'user/'
# NOTE: When adding special `/user/*` endpoints, please remember to update
# `User.reserved_usernames` to prevent URL ambiguity.
urlpatterns = patterns(
    '',
    url(r'^profile/$', r.user_detail_redirect, name='user_detail_redirect'),

    url(r'^settings/$', r.user_profile_settings, name='user_profile_settings'),

    url(r'^achievements/$', r.achievements, name='achievements'),

    url(r'^(?P<username>[\w.@+-]+)/$', r.user_detail, name='user_detail'),

    url(r'^(?P<username>[\w.@+-]+)/request-individual-mapper-status/$',
        r.request_individual_mapper_status,
        name='request_individual_mapper_status'),

    url(r'^(?P<username>[\w.@+-]+)/printable-survey-form/$',
        r.start_form_for_reservation_job,
        name='start_form_for_reservation_job'),

    url(r'^(?P<username>[\w.@+-]+)/printable-map/$',
        r.start_map_for_reservation_job,
        name='start_map_for_reservation_job'),

    url(r'^(?P<username>[\w.@+-]+)/printable-tooldepots/$',
        r.start_map_for_tool_depots_job,
        name='start_map_for_tool_depots_job'),
)
