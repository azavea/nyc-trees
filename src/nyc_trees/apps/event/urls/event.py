# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from apps.core.decorators import is_group_admin, route, has_training
from apps.event.views import (events_list_page, events_list_page_partial,
                              events_list_feed, delete_event, edit_event,
                              event_popup_partial, register_for_event,
                              event_detail, cancel_event_registration,
                              start_event_map_print_job,
                              event_check_in_page, check_in_user_to_event,
                              un_check_in_user_to_event,
                              email_event_registered_users)


# These URLs have the prefix 'event/'
urlpatterns = patterns(
    '',
    url(r'^$',
        route(GET=events_list_page),
        name='events_list_page'),

    url(r'^table/$',
        route(GET=events_list_page_partial),
        name='events_list_page_partial'),

    url(r'^feed/$',
        route(GET=events_list_feed),
        name='events_list_feed'),

    url(r'^(?P<event_url_name>\w+)/$',
        route(GET=event_detail,
              DELETE=is_group_admin(delete_event),
              PUT=is_group_admin(edit_event)),
        name='event_detail'),

    url(r'^(?P<event_url_name>\w+)/popup/$',
        route(GET=event_popup_partial),
        name='event_popup_partial'),

    url(r'^(?P<event_url_name>\w+)/register/$',
        has_training(route(POST=register_for_event,
                           DELETE=cancel_event_registration)),
        name='event_registration'),

    url(r'^(?P<event_url_name>\w+)/printable-map/$',
        has_training(route(POST=start_event_map_print_job)),
        name='start_event_map_print_job'),

    url(r'^(?P<event_url_name>\w+)/checkin/$',
        is_group_admin(route(GET=event_check_in_page)),
        name='event_check_in_page'),

    url(r'^(?P<event_url_name>\w+)/checkin/(?P<username>\w+)/$',
        is_group_admin(route(POST=check_in_user_to_event,
                             DELETE=un_check_in_user_to_event)),
        name='event_check_in'),

    url(r'^(?P<event_url_name>\w+)/email/$',
        is_group_admin(route(POST=email_event_registered_users)),
        name='email_event_registered_users'),
)
