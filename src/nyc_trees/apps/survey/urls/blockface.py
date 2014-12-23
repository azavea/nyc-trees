# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from django_tinsel.decorators import route

from apps.core.decorators import (user_must_be_individual_mapper,
                                  user_must_have_online_training)
from apps.survey.views import (reserve_blockface_page, cancel_reservation,
                               add_blockface_to_cart,
                               remove_blockface_from_cart, blockface_cart_page,
                               reserve_blockfaces,
                               blockface_reservations_confirmation_page,
                               start_survey, submit_survey)


# These URLs have the prefix 'blockface/'
urlpatterns = patterns(
    '',
    url(r'^$',
        user_must_be_individual_mapper(route(GET=reserve_blockface_page)),
        name='reserve_blockface_page'),

    url(r'^(?P<blockface_id>\d+)/cancel-reservation/$',
        user_must_be_individual_mapper(route(POST=cancel_reservation)),
        name='cancel_reservation'),

    url(r'^(?P<blockface_id>\d+)/cart/$',
        user_must_be_individual_mapper(
            route(POST=add_blockface_to_cart,
                  DELETE=remove_blockface_from_cart)),
        name='edit_cart_for_blockface'),

    url(r'^checkout/$',
        user_must_be_individual_mapper(route(GET=blockface_cart_page,
                                             POST=reserve_blockfaces)),
        name='reserve_blockfaces'),

    url(r'^checkout-confirmation/$',
        user_must_be_individual_mapper(
            route(GET=blockface_reservations_confirmation_page)),
        name='blockface_reservations_confirmation_page'),

    url(r'^(?P<blockface_id>\d+)/survey/$',
        user_must_have_online_training(route(GET=start_survey,
                                             POST=submit_survey)),
        name='start_survey'),
)
