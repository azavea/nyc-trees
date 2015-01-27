# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url, include

from apps.home import routes as r
from apps.home.training import (training_summary, getting_started,
                                the_mapping_method,
                                tree_data, tree_surroundings,
                                groups_to_follow)

flatpage_view = 'django.contrib.flatpages.views.flatpage'

urlpatterns = patterns(
    '',
    url(r'^$', r.home_page, name='home_page'),

    url(r'^progress/$', r.progress_page, name='progress_page'),

    url(r'^jobs/(?P<job_id>\d+)/$', r.retrieve_job_status,
        name='retrieve_job_status'),

    url(r'^training/$', **training_summary.pure_kwargs()),                                             # NOQA
    url(r'^training/pure/getting_started/', **getting_started.pure_kwargs()),                          # NOQA
    url(r'^training/pure/the_mapping_method/', **the_mapping_method.pure_kwargs()),                    # NOQA
    url(r'^training/pure/tree_data/', **tree_data.pure_kwargs()),                                      # NOQA
    url(r'^training/pure/tree_surroundings/', **tree_surroundings.pure_kwargs()),                      # NOQA
    url(r'^training/pure/groups_to_follow/$', **groups_to_follow.pure_kwargs()),                       # NOQA
    url(r'^training/progress/the_mapping_method/', **the_mapping_method.previous_step.mark_kwargs()),  # NOQA
    url(r'^training/progress/tree_data/', **tree_data.previous_step.mark_kwargs()),                    # NOQA
    url(r'^training/progress/tree_surroundings/', **tree_surroundings.previous_step.mark_kwargs()),    # NOQA
    url(r'^training/progress/groups_to_follow/$', **groups_to_follow.previous_step.mark_kwargs()),     # NOQA
    url(r'^training/progress/$', **training_summary.previous_step.mark_kwargs()),                      # NOQA

    # "training/pages" instead of "training/pages/" because the
    # flatpages admin interface insists that the "URL" (really a URL
    # segment) start with a leading slash
    url('^training/pages', include('django.contrib.flatpages.urls')),
)
