# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.auth.decorators import login_required

from django_tinsel.decorators import route, render_template, json_api_call
from django_tinsel.utils import decorate as do

from apps.core.decorators import (individual_mapper_do, group_request,
                                  census_admin_do)
from apps.survey import views as v

#####################################
# PROGRESS PAGE ROUTES
#####################################

progress_page = route(GET=do(render_template('survey/progress.html'),
                             v.progress_page))

progress_page_blockface_popup = route(
    GET=do(
        render_template('survey/partials/progress_page_blockface_popup.html'),
        v.progress_page_blockface_popup))

#####################################
# RESERVATION ROUTES
#####################################

reservations = route(
    GET=do(
        login_required,
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

reservations_instructions = do(
    login_required,
    render_template('survey/reservations_instructions.html'),
    v.reservations_instructions)

#####################################
# SURVEY ROUTES
#####################################

survey_detail = individual_mapper_do(
    route(GET=do(render_template('survey/survey_detail.html'),
                 v.survey_detail)))

survey = individual_mapper_do(
    route(GET=do(render_template('survey/survey.html'),
                 v.start_survey),
          POST=do(json_api_call, v.submit_survey)))

survey_from_event = do(
    login_required,
    group_request,
    route(GET=do(render_template('survey/survey.html'),
                 v.start_survey_from_event),
          POST=do(json_api_call, v.submit_survey_from_event)))

flag_survey = do(login_required,
                 route(POST=do(json_api_call, v.flag_survey)))

species_autocomplete_list = route(
    GET=v.species_autocomplete_list)

blockface = route(GET=do(json_api_call, v.blockface))

#####################################
# ADMIN ROUTES
#####################################

admin_territory_page = route(GET=census_admin_do(
    render_template('survey/admin_territory.html'),
    v.admin_territory_page))

admin_blockface_partial = route(
    GET=v.admin_blockface_partial)

admin_blockface_detail_page = route(
    GET=v.admin_blockface_page)

admin_extend_blockface_reservation = route(
    POST=v.admin_extend_blockface_reservation)

admin_blockface_available = route(
    GET=v.admin_blockface_available)
