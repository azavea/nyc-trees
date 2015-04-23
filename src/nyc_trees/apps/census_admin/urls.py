# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from apps.census_admin import routes as r


# These URLs have the prefix 'census_admin/'
urlpatterns = patterns(
    '',
    url(r'^upload-group-polygons/$', r.upload_group_polygons,
        name='upload_group_polygons'),
)
