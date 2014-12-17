# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from apps.event.routes import (events_list_page,
                               events_list_page_partial,
                               events_list_feed)
from apps.event.event_list import all_events, immediate_events

# These URLs have the prefix 'event/'
urlpatterns = patterns(
    '',
    url(r'^$',
        events_list_page, name='events_list_page'),

    url(r'^table/$',
        events_list_page_partial, name='events_list_page_partial'),

    url(r'^user-events/$',
        immediate_events.endpoint, name=immediate_events.url_name()),

    url(r'^all-events/$', all_events.endpoint, name=all_events.url_name()),

    url(r'^feed/$',
        events_list_feed, name='events_list_feed'),
)
