# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from apps.core.decorators import route, is_logged_in, is_group_admin
from apps.users.views import (group_list_page, group_detail, edit_group,
                              follow_group, unfollow_group,
                              start_group_map_print_job,
                              group_mapping_priveleges_page,
                              give_user_mapping_priveleges,
                              remove_user_mapping_priveleges)


# These URLs have the prefix 'group/'
urlpatterns = patterns(
    '',
    url(r'^$',
        route(GET=group_list_page),
        name='group_list_page'),

    url(r'^(?P<group_name>\w+)/$',
        route(GET=group_detail,
              PUT=is_group_admin(edit_group)),
        name='group_detail'),

    url(r'^(?P<group_name>\w+)/follow/$',
        is_logged_in(route(POST=follow_group)),
        name='follow_group'),

    url(r'^(?P<group_name>\w+)/unfollow/$',
        is_logged_in(route(POST=unfollow_group)),
        name='unfollow_group'),

    url(r'^(?P<group_name>\w+)/printable-map/$',
        # TODO: should this have group_admin()
        route(POST=start_group_map_print_job),
        name='start_group_map_print_job'),

    url(r'^(?P<group_name>\w+)/individual-mapper/$',
        is_group_admin(route(GET=group_mapping_priveleges_page)),
        name='group_mapping_priveleges_page'),

    url(r'^(?P<group_name>\w+)/individual-mapper/(?P<username>\w+)/$',
        is_group_admin(route(PUT=give_user_mapping_priveleges,
                             DELETE=remove_user_mapping_priveleges)),
        name='edit_user_mapping_priveleges'),
)
