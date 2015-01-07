# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from apps.core.routes import js_settings


urlpatterns = patterns(
    '',
    url(r'^js-settings/$', js_settings, name='js_settings'),
)
