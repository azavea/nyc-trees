# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url, include

from apps.home import routes as r

flatpage_view = 'django.contrib.flatpages.views.flatpage'

urlpatterns = patterns(
    '',
    url(r'^$', r.home_page, name='home_page'),

    url(r'^progress/$', r.progress_page, name='progress_page'),

    url(r'^jobs/(?P<job_id>\d+)/$', r.retrieve_job_status,
        name='retrieve_job_status'),

    # pure training pages
    url(r'^training/$', r.training_list_page, name="training_list_page"),
    url(r'^training/pages/getting_started/',
        flatpage_view, {'url': '/getting_started/'}),
    url(r'^training/pages/the_mapping_method/',
        flatpage_view, {'url': '/the_mapping_method/'}),
    url(r'^training/pages/tree_data/',
        flatpage_view, {'url': '/tree_data/'}),
    url(r'^training/pages/tree_surroundings/',
        flatpage_view, {'url': '/tree_surroundings/'}),
    url(r'^training/groups_to_follow/$', r.groups_to_follow),

    # "training" instead of "training/" because the flatpages admin interface
    # insists that the "URL" (really a URL segment) start with a leading slash
    url(r'^training(?P<url>.*/)$', include('django.contrib.flatpages.urls')),
    # TODO: should we even still allow arbitrary flat pages?
    # "training/pages" instead of "training/pages/" because the
    # flatpages admin interface insists that the "URL" (really a URL
    # segment) start with a leading slash
    url('^training/pages', include('django.contrib.flatpages.urls')),
)
