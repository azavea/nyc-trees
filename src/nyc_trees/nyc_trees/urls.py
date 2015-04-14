# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),

    url(r'^', include('apps.home.urls')),
    url(r'^accounts/', include('apps.login.urls.accounts')),
    url(r'^blockedge/', include('apps.survey.urls.blockface')),
    url(r'^census_admin/', include('apps.census_admin.urls')),
    url(r'^census_admin/', include('apps.survey.urls.census_admin')),
    url(r'^event/', include('apps.event.urls.event')),
    url(r'^geocode/', include('apps.geocode.urls')),
    url(r'^group/', include('apps.event.urls.group')),
    url(r'^group/', include('apps.users.urls.group')),
    url(r'^login/', include('apps.login.urls.login')),
    url(r'^survey/', include('apps.survey.urls.survey')),
    url(r'^user/', include('apps.users.urls.user')),
)
