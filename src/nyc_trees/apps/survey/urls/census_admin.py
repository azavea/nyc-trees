# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from apps.survey import routes as r


# These URLs have the prefix 'census_admin/'
urlpatterns = patterns(
    '',
    url(r'^census_zones/$', r.admin_territory_page,
        name='admin_territory_page'),
)
