# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from django_tinsel.decorators import route

from apps.users.views.user import (user_detail, update_user,
                                   request_individual_mapper_status,
                                   start_form_for_reservation_job,
                                   start_map_for_reservation_job,
                                   start_map_for_tool_depots_job,
                                   user_detail_redirect)


# These URLs have the prefix 'user/'
urlpatterns = patterns(
    '',
    url(r'^profile/$', login_required(route(GET=user_detail_redirect)),
        name='user_detail_redirect'),

    url(r'^(?P<username>\w+)/$',
        route(GET=user_detail,
              PUT=login_required(update_user)),
        name='user_detail'),

    url(r'^(?P<username>\w+)/request-individual-mapper-status/$',
        login_required(route(POST=request_individual_mapper_status)),
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
