# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url
from apps.users.routes import group as r
from apps.users.views.group import group_edit_events, group_detail_events

# These URLs have the prefix 'group/'
urlpatterns = patterns(
    '',
    url(r'^$', r.group_list_page, name='group_list_page'),

    url(r'^(?P<group_slug>[\w-]+)/$', r.group_detail, name='group_detail'),

    url(r'^(?P<group_slug>[\w-]+)/edit/$', r.group_edit, name='group_edit'),

    url(r'^(?P<group_slug>[\w-]+)/edit/events/$',
        group_edit_events.endpoint, name=group_edit_events.url_name()),

    url(r'^(?P<group_slug>[\w-]+)/follow/$',
        r.follow_group, name='follow_group'),

    url(r'^(?P<group_slug>[\w-]+)/unfollow/$',
        r.unfollow_group, name='unfollow_group'),

    url(r'^(?P<group_slug>[\w-]+)/printable-map/$',
        r.start_group_map_print_job,
        name='start_group_map_print_job'),

    url(r'^(?P<group_slug>[\w-]+)/individual-mapper/(?P<username>\w+)/$',
        r.edit_user_mapping_priveleges,
        name='edit_user_mapping_priveleges'),

    # Keep in sync with src/nyc_trees/js/src/group_detail.js
    # Keep in sync with src/nyc_trees/js/src/reserveBlockfacePage.js
    url(r'^(?P<group_slug>[\w-]+)/request-trusted-mapper-status/$',
        r.request_mapper_status,
        name='request_mapper_status'),

    url(r'^(?P<group_slug>[\w-]+)/events/$',
        group_detail_events.endpoint, name=group_detail_events.url_name()),
)
