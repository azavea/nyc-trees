# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url, include

from apps.home import routes as r
from apps.home.training import routes as tr
from apps.home.training import (training_summary, getting_started,
                                the_mapping_method,
                                tree_data, tree_surroundings,
                                wrapping_up, intro_quiz)

flatpage_view = 'django.contrib.flatpages.views.flatpage'

urlpatterns = patterns(
    '',
    url(r'^$', r.home_page, name='home_page'),

    url(r'^faq/$', r.about_faq_page, name='about_faq_page'),

    url(r'^health-check/$', include('watchman.urls')),

    url(r'^individual-mapper-instructions/$',
        r.individual_mapper_instructions,
        name='individual_mapper_instructions'),

    url(r'^trusted-mapper-request-sent/$',
        r.trusted_mapper_request_sent,
        name='trusted_mapper_request_sent'),

    url(r'^jobs/(?P<job_id>\d+)/$', r.retrieve_job_status,
        name='retrieve_job_status'),

    # `groups_to_follow` is managed out of band from the training workflow,
    # it is only merged in as part of the presentation layer.
    url(r'^training/groups_to_follow/$',
        tr.groups_to_follow, name='groups_to_follow'),

    url(r'^training/$', **training_summary.pure_kwargs()),                                             # NOQA
    url(r'^training/pure/getting_started/', **getting_started.pure_kwargs()),                          # NOQA
    url(r'^training/pure/the_mapping_method/', **the_mapping_method.pure_kwargs()),                    # NOQA
    url(r'^training/pure/tree_data/', **tree_data.pure_kwargs()),                                      # NOQA
    url(r'^training/pure/tree_surroundings/', **tree_surroundings.pure_kwargs()),                      # NOQA
    url(r'^training/pure/wrapping_up/', **wrapping_up.pure_kwargs()),                                  # NOQA
    url(r'^training/pure/intro_quiz/', **intro_quiz.pure_kwargs()),                                    # NOQA

    # getting_started does not have a mark endpoint because it has no trackable previous step          # NOQA
    url(r'^training/progress/the_mapping_method/', **the_mapping_method.previous_step.mark_kwargs()),  # NOQA
    url(r'^training/progress/tree_data/', **tree_data.previous_step.mark_kwargs()),                    # NOQA
    url(r'^training/progress/tree_surroundings/', **tree_surroundings.previous_step.mark_kwargs()),    # NOQA
    url(r'^training/progress/wrapping_up/', **wrapping_up.previous_step.mark_kwargs()),                # NOQA
    url(r'^training/progress/intro_quiz/$', **intro_quiz.previous_step.mark_kwargs()),                 # NOQA
    url(r'^training/progress/$', **training_summary.previous_step.mark_kwargs()),                      # NOQA

    url(r'^training/instructions', tr.training_instructions,
        name='training_instructions'),

    # "training/pages" instead of "training/pages/" because the
    # flatpages admin interface insists that the "URL" (really a URL
    # segment) start with a leading slash
    url('^training/pages', include('django.contrib.flatpages.urls')),
)
