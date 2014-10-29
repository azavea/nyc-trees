# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from apps.core.decorators import route
from apps.survey.views import species_autocomplete_list


# These URLs have the prefix 'species/'
urlpatterns = patterns(
    '',
    url(r'^$',
        route(GET=species_autocomplete_list),
        name='species_autocomplete_list'),
)
