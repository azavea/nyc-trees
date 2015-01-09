# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url, include

from apps.home import routes as r


urlpatterns = patterns(
    '',
    url(r'^$', r.home_page, name='home_page'),

    url(r'^progress/$', r.progress_page, name='progress_page'),

    url(r'^jobs/(?P<job_id>\d+)/$', r.retrieve_job_status,
        name='retrieve_job_status'),

    url(r'^training/$', r.training_list_page, name="training_list_page"),

    url(r'^training/groups_to_follow/$', r.groups_to_follow),

    # "training" instead of "training/" because the flatpages admin interface
    # insists that the "URL" (really a URL segment) start with a leading slash
    url(r'^training(?P<url>.*/)$', include('django.contrib.flatpages.urls')),
)
