# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from django_tinsel.decorators import route, render_template
from django_tinsel.utils import decorate as do

from apps.event.views import (events_list_page, events_list_page_partial,
                              events_list_feed)


# These URLs have the prefix 'event/'
urlpatterns = patterns(
    '',
    url(r'^$',
        route(GET=do(
            render_template('event/event_list.html'),
            events_list_page)),
        name='events_list_page'),

    url(r'^table/$',
        route(GET=events_list_page_partial),
        name='events_list_page_partial'),

    url(r'^feed/$',
        route(GET=events_list_feed),
        name='events_list_feed'),
)
