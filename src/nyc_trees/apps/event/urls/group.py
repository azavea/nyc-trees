# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from apps.core.decorators import is_group_admin, route
from apps.event.views import (event_dashboard, add_event, event_detail)


# These URLs have the prefix 'group/'
urlpatterns = patterns(
    '',
    url(r'^(?P<group_name>\w+)/event/$',
        is_group_admin(route(GET=event_dashboard,
                             POST=add_event)),
        name='events'),

    url(r'^(?P<group_name>\w+)/event/(?P<event_id>\d+)/$',
        route(GET=event_detail),
        name='group_event_detail'),
    )
