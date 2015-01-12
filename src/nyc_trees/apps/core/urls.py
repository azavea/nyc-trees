# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from apps.core.routes import settings_js


urlpatterns = patterns(
    '',
    url(r'^settings.js$', settings_js, name='settings_js'),
)
