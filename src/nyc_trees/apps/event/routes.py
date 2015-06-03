# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.auth.decorators import login_required

from django_tinsel.decorators import route, render_template, json_api_call

from django_tinsel.utils import decorate as do

from apps.core.decorators import (user_must_have_online_training,
                                  group_request, group_admin_do)
from apps.event import views as v

#####################################
# EVENT ROUTES
#####################################

events_list_page = route(
    GET=do(
        render_template('event/event_list_page.html'),
        v.events_list_page))

events_list_feed = route(GET=do(json_api_call, v.events_list_feed))

future_events_geojson = route(GET=do(json_api_call, v.future_events_geojson))

#####################################
# GROUP ROUTES
#####################################

add_event = group_admin_do(render_template('event/add_event.html'),
                           route(GET=v.add_event_page,
                                 POST=v.add_event))

event_detail = do(group_request,
                  route(GET=do(render_template('event/event_detail.html'),
                               v.event_detail)))

event_edit = group_admin_do(render_template('event/edit_event.html'),
                            route(GET=v.edit_event_page,
                                  POST=v.edit_event))

event_email = group_admin_do(render_template('event/email_rsvps.html'),
                             route(GET=v.event_email_page,
                                   POST=v.event_email))

event_popup_partial = do(
    render_template('event/partials/event_popup.html'),
    group_request,
    route(GET=v.event_popup_partial))

event_registration = do(login_required,
                        group_request,
                        user_must_have_online_training,
                        render_template('event/partials/rsvp.html'),
                        route(POST=v.register_for_event,
                              DELETE=v.cancel_event_registration))

printable_event_map = do(
    group_request,
    route(GET=do(render_template('event/printable_event_map.html'),
                 v.printable_event_map)))

event_admin_check_in_page = group_admin_do(
    route(GET=do(render_template('event/admin_checkin.html'),
                 v.event_admin_check_in_page)))

event_user_check_in_page = do(
    login_required,
    group_request,
    route(GET=do(render_template('event/user_checkin.html'),
                 v.event_user_check_in_page)))

event_user_check_in_poll = do(
    login_required,
    group_request,
    route(GET=do(json_api_call, v.event_user_check_in_poll)))

check_in_user_to_event = group_admin_do(
    render_template('event/partials/checkin_button.html'),
    route(POST=v.check_in_user_to_event,
          DELETE=v.check_in_user_to_event))

increase_rsvp_limit = route(POST=group_admin_do(json_api_call,
                                                v.increase_rsvp_limit))

event_map_poll = route(GET=do(group_request,
                              json_api_call,
                              v.event_map_poll))

event_email_unsubscribe = route(
    GET=do(group_request,
           render_template('event/event_email_unsubscribed.html'),
           v.event_email_unsubscribe))

event_email_invalid_token = route(
    GET=do(group_request,
           render_template('event/invalid_token.html'),
           v.event_email_invalid_token))
