# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from django_tinsel.decorators import route

from apps.core.decorators import census_admin_do
from apps.survey import routes as r

from apps.survey.views import (admin_blockface_partial,
                               admin_blockface_detail_page,
                               admin_extend_blockface_reservation,
                               admin_blockface_available)


# These URLs have the prefix 'census_admin/'
urlpatterns = patterns(
    '',
    url(r'^territory/$', r.admin_territory_page,
        name='admin_territory_page'),

    url(r'^blockface-partial/$',
        census_admin_do(route(GET=admin_blockface_partial)),
        name='admin_blockface_partial'),

    url(r'^blockface/(?P<blockface_id>\d+)/$',
        census_admin_do(route(GET=admin_blockface_detail_page)),
        name='admin_blockface_detail_page'),

    url(r'^blockface/(?P<blockface_id>\d+)/extend-reservation/$',
        census_admin_do(route(
            POST=admin_extend_blockface_reservation)),
        name='admin_extend_blockface_reservation'),

    url(r'^blockface/(?P<blockface_id>\d+)/set-available/$',
        census_admin_do(route(POST=admin_blockface_available)),
        name='admin_blockface_available'),
)
