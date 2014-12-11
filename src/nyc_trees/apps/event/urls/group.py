# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from django_tinsel.decorators import route

from apps.core.decorators import is_group_admin, has_training
from apps.event.views import (
    event_dashboard, add_event, add_event_page, delete_event, edit_event,
    event_popup_partial, register_for_event, event_detail, edit_event_page,
    cancel_event_registration, start_event_map_print_job, event_check_in_page,
    check_in_user_to_event, un_check_in_user_to_event,
    email_event_registered_users)


# These URLs have the prefix 'group/'
urlpatterns = patterns(
    '',
    url(r'^(?P<group_slug>[\w-]+)/event/$',
        is_group_admin(route(GET=event_dashboard)),
        name='events'),

    url(r'^(?P<group_slug>[\w-]+)/add-event/$',
        is_group_admin(route(GET=add_event_page,
                             POST=add_event)),
        name='add_event'),

    url(r'^(?P<group_slug>[\w-]+)/event/(?P<event_slug>[\w-]+)/$',
        route(GET=event_detail,
              DELETE=is_group_admin(delete_event)),
        name='event_detail'),

    url(r'^(?P<group_slug>[\w-]+)/event/(?P<event_slug>[\w-]+)/edit/$',
        route(GET=is_group_admin(edit_event_page),
              PUT=is_group_admin(edit_event)),
        name='event_edit'),

    url(r'^(?P<group_slug>[\w-]+)/event/(?P<event_slug>[\w-]+)/popup/$',
        route(GET=event_popup_partial),
        name='event_popup_partial'),

    url(r'^(?P<group_slug>[\w-]+)/event/(?P<event_slug>[\w-]+)/register/$',
        has_training(route(POST=register_for_event,
                           DELETE=cancel_event_registration)),
        name='event_registration'),

    url(r'^(?P<group_slug>[\w-]+)/event/'
        r'(?P<event_slug>[\w-]+)/printable-map/$',
        has_training(route(POST=start_event_map_print_job)),
        name='start_event_map_print_job'),

    url(r'^(?P<group_slug>[\w-]+)/event/(?P<event_slug>[\w-]+)/checkin/$',
        is_group_admin(route(GET=event_check_in_page)),
        name='event_check_in_page'),

    url(r'^(?P<group_slug>[\w-]+)/event/'
        r'(?P<event_slug>[\w-]+)/checkin/(?P<username>[^/]+)/$',
        is_group_admin(route(POST=check_in_user_to_event,
                             DELETE=un_check_in_user_to_event)),
        name='event_check_in'),

    url(r'^(?P<group_slug>[\w-]+)/event/(?P<event_slug>[\w-]+)/email/$',
        is_group_admin(route(POST=email_event_registered_users)),
        name='email_event_registered_users'),
)
