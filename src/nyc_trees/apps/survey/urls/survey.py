# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from django_tinsel.decorators import route

from apps.core.decorators import has_training
from apps.survey.views import choose_blockface_survey_page


# These URLs have the prefix 'survey/'
urlpatterns = patterns(
    '',
    # The choose_blockface_survey_page will have a GET parameter of
    # blockface_id, which is used to change the starting map location
    url(r'^$',
        has_training(route(GET=choose_blockface_survey_page)),
        name='choose_blockface_survey_page'),
)
