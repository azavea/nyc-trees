# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from apps.geocode.routes import geocode

urlpatterns = patterns(
    '',
    url(r'^$', geocode, name='geocode'),
)
