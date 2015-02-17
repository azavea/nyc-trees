# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from apps.survey.routes import (reserve_blockface_page, cancel_reservation,
                                reserve_blockfaces, survey, reservations,
                                reserved_blockface_popup,
                                reservations_instructions,
                                blockface_reservations_confirmation_page,
                                blockface, progress_page,
                                progress_page_blockface_popup)


# These URLs have the prefix 'blockface/'
urlpatterns = patterns(
    '',
    url(r'^progress/$', progress_page, name='progress_page'),

    url(r'^$', reservations, name='reservations'),

    url(r'^reserve/$', reserve_blockface_page, name='reserve_blockface_page'),

    url(r'^reservations-instructions/$', reservations_instructions,
        name='reservations_instructions'),

    url(r'^(?P<blockface_id>\d+)/cancel-reservation/$', cancel_reservation,
        name='cancel_reservation'),

    # Note: changes here must be kept in sync with
    # src/nyc_trees/js/src/reservationPage.js
    url(r'^(?P<blockface_id>\d+)/reservation-popup/$',
        reserved_blockface_popup, name='reserved_blockface_popup'),

    url(r'^checkout/$', reserve_blockfaces, name='reserve_blockfaces'),

    url(r'^checkout-confirmation/$', blockface_reservations_confirmation_page,
        name='blockface_reservations_confirmation_page'),

    url(r'^(?P<blockface_id>\d+)/survey/$', survey, name='survey'),

    # Note: this must be kept in sync with the hardcoded url in
    # js/src/reservationPage.js
    url(r'^(?P<blockface_id>\d+)/$', blockface,
        name='blockface'),
)
