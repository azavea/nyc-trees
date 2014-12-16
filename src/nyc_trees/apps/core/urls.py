# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from django_tinsel.decorators import route


# These URLs have the prefix 'quiz/'
urlpatterns = patterns(
    '',
    url(r'^js-settings/$',
        route(GET=TemplateView.as_view(template_name='core/settings.js',
                                       content_type='application/javascript')),
        name='js_settings'),
)
