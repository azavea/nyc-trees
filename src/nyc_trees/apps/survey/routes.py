# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django_tinsel.decorators import route, render_template, json_api_call
from django_tinsel.utils import decorate as do

from apps.core.decorators import individual_mapper_do

from apps.survey import views as v

#####################################
# RESERVATION ROUTES
#####################################

reservations = route(
    GET=individual_mapper_do(
        render_template('survey/reservations.html'),
        v.reservations_page))

reserve_blockface_page = route(
    GET=individual_mapper_do(
        render_template('survey/reserve_blockface.html'),
        v.reserve_blockfaces_page))

reserved_blockface_popup = route(
    GET=individual_mapper_do(
        render_template('survey/partials/reserved_blockface_popup.html'),
        v.reserved_blockface_popup))

cancel_reservation = route(
    GET=individual_mapper_do(
        json_api_call,
        v.cancel_reservation))

reserve_blockfaces = individual_mapper_do(
    render_template('survey/blockface_cart.html'),
    route(POST=v.blockface_cart_page))

blockface_reservations_confirmation_page = individual_mapper_do(
    render_template('survey/reserve_blockface_confirmation.html'),
    route(POST=v.confirm_blockface_reservations))

#####################################
# SURVEY ROUTES
#####################################

survey = individual_mapper_do(
    route(GET=v.start_survey,
          POST=v.submit_survey))

choose_blockface_survey_page = route(
    GET=individual_mapper_do(
        v.choose_blockface_survey_page))

species_autocomplete_list = route(
    GET=v.species_autocomplete_list)

blockface = route(GET=do(json_api_call, v.blockface))

#####################################
# ADMIN ROUTES
#####################################

admin_blockface_page = route(
    GET=v.admin_blockface_page)

admin_blockface_partial = route(
    GET=v.admin_blockface_partial)

admin_blockface_detail_page = route(
    GET=v.admin_blockface_page)

admin_extend_blockface_reservation = route(
    POST=v.admin_extend_blockface_reservation)

admin_blockface_available = route(
    GET=v.admin_blockface_available)
