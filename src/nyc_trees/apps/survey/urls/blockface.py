# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from apps.survey.routes import (reserve_blockface_page, cancel_reservation,
                                edit_cart_for_blockface, reserve_blockfaces,
                                blockface_reservations_confirmation_page,
                                survey, reservations, reserved_blockface_popup)


# These URLs have the prefix 'blockface/'
urlpatterns = patterns(
    '',
    url(r'^$', reservations, name='reservations'),

    url(r'^reserve/$', reserve_blockface_page, name='reserve_blockface_page'),

    url(r'^(?P<blockface_id>\d+)/cancel-reservation/$', cancel_reservation,
        name='cancel_reservation'),

    url(r'^(?P<blockface_id>\d+)/cart/$', edit_cart_for_blockface,
        name='edit_cart_for_blockface'),

    # Note: changes here must be kept in sync with
    # src/nyc_trees/js/src/reservationPage.js
    url(r'^(?P<blockface_id>\d+)/reservation-popup/$',
        reserved_blockface_popup, name='reserved_blockface_popup'),

    url(r'^checkout/$', reserve_blockfaces, name='reserve_blockfaces'),

    url(r'^checkout-confirmation/$', blockface_reservations_confirmation_page,
        name='blockface_reservations_confirmation_page'),

    url(r'^(?P<blockface_id>\d+)/survey/$', survey, name='survey'),
)
