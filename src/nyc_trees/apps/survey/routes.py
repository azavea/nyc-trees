# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import login_required

from django_tinsel.decorators import route, render_template, json_api_call
from django_tinsel.utils import decorate as do

from apps.core.decorators import (individual_mapper_do, group_request,
                                  census_admin_do, update_with)
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

printable_reservations_map = route(
    GET=do(
        login_required,
        render_template('survey/printable_reservations_map.html'),
        v.printable_reservations_page))

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

reservations_map_pdf_poll = route(GET=do(login_required,
                                         json_api_call,
                                         v.reservations_map_pdf_poll))

#####################################
# SURVEY ROUTES
#####################################


def _add_survey_url(request, *args, **kwargs):
    return {'survey_url': reverse('survey')}


def _add_event_url(request, event_slug, *args, **kwargs):
    url = reverse('survey_from_event',
                  kwargs={'group_slug': request.group.slug,
                          'event_slug': event_slug})
    return {'survey_url': url}

survey_detail = individual_mapper_do(
    route(GET=do(render_template('survey/survey_detail.html'),
                 v.survey_detail)))

confirm_survey = individual_mapper_do(
    route(GET=do(render_template('survey/survey_detail.html'),
                 update_with({'show_controls': True}),
                 update_with(_add_survey_url),
                 v.survey_detail)))

confirm_survey_from_event = do(
    login_required,
    group_request,
    route(GET=do(render_template('survey/survey_detail.html'),
                 update_with({'show_controls': True}),
                 update_with(_add_event_url),
                 v.survey_detail_from_event)))

survey = individual_mapper_do(
    route(GET=do(render_template('survey/survey.html'),
                 update_with(_add_survey_url),
                 v.start_survey),
          POST=do(json_api_call, v.submit_survey)))

survey_from_event = do(
    login_required,
    group_request,
    route(GET=do(render_template('survey/survey.html'),
                 update_with(_add_event_url),
                 v.start_survey_from_event),
          POST=do(json_api_call, v.submit_survey_from_event)))

flag_survey = do(login_required,
                 route(POST=do(json_api_call, v.flag_survey)))

release_blockface = do(login_required,
                       route(POST=do(json_api_call, v.release_blockface)))

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
    GET=v.admin_blockface_detail_page)

admin_extend_blockface_reservation = route(
    POST=v.admin_extend_blockface_reservation)

admin_blockface_available = route(
    GET=v.admin_blockface_available)
