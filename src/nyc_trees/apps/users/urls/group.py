# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from django_tinsel.decorators import route

from apps.core.decorators import is_group_admin
from apps.users.views.group import (group_list_page, group_detail, edit_group,
                                    follow_group, unfollow_group,
                                    start_group_map_print_job,
                                    give_user_mapping_priveleges,
                                    remove_user_mapping_priveleges,
                                    update_group_settings)


# These URLs have the prefix 'group/'
urlpatterns = patterns(
    '',
    url(r'^$',
        route(GET=group_list_page),
        name='group_list_page'),

    url(r'^(?P<group_slug>[\w-]+)/$',
        route(GET=group_detail),
        name='group_detail'),

    url(r'^(?P<group_slug>[\w-]+)/edit/$',
        is_group_admin(
            route(GET=edit_group,
                  POST=update_group_settings)),
        name='group_edit'),

    url(r'^(?P<group_slug>[\w-]+)/follow/$',
        login_required(route(POST=follow_group)),
        name='follow_group'),

    url(r'^(?P<group_slug>[\w-]+)/unfollow/$',
        login_required(route(POST=unfollow_group)),
        name='unfollow_group'),

    url(r'^(?P<group_slug>[\w-]+)/printable-map/$',
        # TODO: should this have group_admin()
        route(POST=start_group_map_print_job),
        name='start_group_map_print_job'),

    url(r'^(?P<group_slug>[\w-]+)/individual-mapper/(?P<username>\w+)/$',
        is_group_admin(route(PUT=give_user_mapping_priveleges,
                             DELETE=remove_user_mapping_priveleges)),
        name='edit_user_mapping_priveleges'),
)
