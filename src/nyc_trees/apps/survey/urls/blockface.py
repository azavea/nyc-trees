# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from apps.survey.routes import (
    reserve_blockface_page, reserve_blockfaces, reservations_instructions,
    blockface, progress_page, blockface_reservations_confirmation_page,
    progress_page_blockface_popup, printable_reservations_map,
    reservations_map_pdf_poll, user_reserved_blockfaces_geojson,
    group_borders_geojson, group_popup
)


# These URLs have the prefix 'blockedge/'
urlpatterns = patterns(
    '',
    url(r'^progress/$', progress_page, name='progress_page'),

    url(r'^printable-map/$', printable_reservations_map,
        name='printable_reservations_map'),

    url(r'^reserve/$', reserve_blockface_page, name='reservations'),

    url(r'^reservations-instructions/$', reservations_instructions,
        name='reservations_instructions'),

    # Note: changes here must be kept in sync with
    # src/nyc_trees/js/src/reserveBlockfacePage.js
    url(r'^reserved-blockedges.json$', user_reserved_blockfaces_geojson),

    # Note: changes here must be kept in sync with
    # src/nyc_trees/js/src/progressPage.js
    url(r'^(?P<blockface_id>\d+)/progress-page-blockedge-popup/$',
        progress_page_blockface_popup, name='progress_blockface_popup'),

    url(r'^checkout/$', reserve_blockfaces, name='reserve_blockfaces'),

    url(r'^checkout-confirmation/$', blockface_reservations_confirmation_page,
        name='blockface_reservations_confirmation_page'),

    # Note: this must be kept in sync with the hardcoded url in
    # js/src/mapUtil.js
    url(r'^(?P<blockface_id>\d+)/$', blockface,
        name='blockface'),

    url(r'^map-poll/$', reservations_map_pdf_poll,
        name='reservations_map_pdf_poll'),

    url(r'^group-popup/(?P<group_slug>[\w-]+)/$', group_popup,
        name='group_popup'),

    url(r'^group-borders.json$', group_borders_geojson, name='group_borders')
)
