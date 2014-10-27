# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from apps.core.decorators import route, is_logged_in
from apps.users.views import (user_detail, update_user,
                              request_individual_mapper_status,
                              start_form_for_reservation_job,
                              start_map_for_reservation_job,
                              start_map_for_tool_depots_job)


# These URLs have the prefix 'user/'
urlpatterns = patterns(
    '',
    url(r'^(?P<username>\w+)/$',
        route(GET=user_detail,
              PUT=is_logged_in(update_user)),
        name='user_detail'),

    url(r'^(?P<username>\w+)/request-individual-mapper-status/$',
        is_logged_in(route(POST=request_individual_mapper_status)),
        name='request_individual_mapper_status'),

    url(r'^(?P<username>\w+)/printable-survey-form/$',
        route(POST=start_form_for_reservation_job),
        name='start_form_for_reservation_job'),

    url(r'^(?P<username>\w+)/printable-map/$',
        route(POST=start_map_for_reservation_job),
        name='start_map_for_reservation_job'),

    url(r'^(?P<username>\w+)/printable-tooldepots/$',
        route(POST=start_map_for_tool_depots_job),
        name='start_map_for_tool_depots_job'),
)
