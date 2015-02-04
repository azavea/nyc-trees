# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from apps.event.routes import (add_event, event_detail,
                               event_edit, event_popup_partial,
                               event_registration, start_event_map_print_job,
                               event_admin_check_in_page,
                               check_in_user_to_event,
                               email_event_registered_users, event_email,
                               increase_rsvp_limit, event_user_check_in_page)

# These URLs have the prefix 'group/'
urlpatterns = patterns(
    '',
    url(r'^(?P<group_slug>[\w-]+)/add-event/$',
        add_event, name='add_event'),

    url(r'^(?P<group_slug>[\w-]+)/event/(?P<event_slug>[\w-]+)/$',
        event_detail, name='event_detail'),

    url(r'^(?P<group_slug>[\w-]+)/event/(?P<event_slug>[\w-]+)/edit/$',
        event_edit, name='event_edit'),

    url(r'^(?P<group_slug>[\w-]+)/event/(?P<event_slug>[\w-]+)/email/$',
        event_email, name='event_email'),

    url(r'^(?P<group_slug>[\w-]+)/event/(?P<event_slug>[\w-]+)/popup/$',
        event_popup_partial, name='event_popup_partial'),

    url(r'^(?P<group_slug>[\w-]+)/event/(?P<event_slug>[\w-]+)/register/$',
        event_registration, name='event_registration'),

    url(r'^(?P<group_slug>[\w-]+)/event/'
        r'(?P<event_slug>[\w-]+)/printable-map/$',
        start_event_map_print_job, name='start_event_map_print_job'),

    url(r'^(?P<group_slug>[\w-]+)/event/(?P<event_slug>[\w-]+)/checkin/$',
        event_admin_check_in_page, name='event_admin_check_in_page'),

    url(r'^(?P<group_slug>[\w-]+)/event/(?P<event_slug>[\w-]+)/arrive/$',
        event_user_check_in_page, name='event_user_check_in_page'),

    url(r'^(?P<group_slug>[\w-]+)/event/'
        r'(?P<event_slug>[\w-]+)/checkin/(?P<username>[^/]+)/$',
        check_in_user_to_event, name='check_in_user_to_event'),

    url(r'^(?P<group_slug>[\w-]+)/event/'
        r'(?P<event_slug>[\w-]+)/increase_rsvp_limit/$',
        increase_rsvp_limit, name='increase_rsvp_limit'),

    url(r'^(?P<group_slug>[\w-]+)/event/(?P<event_slug>[\w-]+)/email/$',
        email_event_registered_users, name='email_event_registered_users'),
)
