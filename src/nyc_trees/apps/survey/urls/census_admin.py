# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from django_tinsel.decorators import route

from apps.core.decorators import is_census_admin
from apps.survey.views import (admin_blockface_page,
                               admin_blockface_partial,
                               admin_blockface_detail_page,
                               admin_extend_blockface_reservation,
                               admin_blockface_available)


# These URLs have the prefix 'census_admin/'
urlpatterns = patterns(
    '',
    url(r'^blockface/$',
        is_census_admin(route(GET=admin_blockface_page)),
        name='admin_blockface_page'),

    url(r'^blockface-partial/$',
        is_census_admin(route(GET=admin_blockface_partial)),
        name='admin_blockface_partial'),

    url(r'^blockface/(?P<blockface_id>\d+)/$',
        is_census_admin(route(GET=admin_blockface_detail_page)),
        name='admin_blockface_detail_page'),

    url(r'^blockface/(?P<blockface_id>\d+)/extend-reservation/$',
        is_census_admin(route(POST=admin_extend_blockface_reservation)),
        name='admin_extend_blockface_reservation'),

    url(r'^blockface/(?P<blockface_id>\d+)/set-available/$',
        is_census_admin(route(POST=admin_blockface_available)),
        name='admin_blockface_available'),
)
