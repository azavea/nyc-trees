# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from django_tinsel.decorators import route

from apps.home.views import home_page, progress_page, retrieve_job_status


urlpatterns = patterns(
    '',
    url(r'^$',
        route(GET=home_page),
        name='home_page'),

    url(r'^progress/$',
        route(GET=progress_page),
        name='progress_page'),

    url(r'^jobs/(?P<job_id>\d+)/$',
        route(GET=retrieve_job_status),
        name='retrieve_job_status'),

    # TODO: The following are all good candidates for the Django flatpages app
    #
    # url(r'^faq/$', route(GET=faq_page)),
    # url(r'^about/$', route(GET=about_page)),
    # url(r'^training/$', route(GET=training_material_list_page)),
    # url(r'^training/(?P<training_material_url_name>\w+)/$',
    #     route(GET=training_material_detail_page)),
)
