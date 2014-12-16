# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django_tinsel.decorators import route, render_template
from django_tinsel.utils import decorate as do

from apps.core.decorators import is_group_admin, has_training
from apps.event import views as v

#####################################
# EVENT ROUTES
#####################################

events_list_page = route(
    GET=do(
        render_template('event/event_list.html'),
        v.events_list_page))

events_list_page_partial = route(GET=v.events_list_page_partial)

events_list_feed = route(GET=v.events_list_feed)

#####################################
# GROUP ROUTES
#####################################

events = is_group_admin(route(GET=v.event_dashboard))

add_event = do(is_group_admin,
               render_template('event/add_event.html'),
               route(GET=v.add_event_page,
                     POST=v.add_event))

event_detail = route(GET=do(render_template('event/event_detail.html'),
                            v.event_detail),
                     DELETE=is_group_admin(v.delete_event))

event_edit = route(GET=do(render_template('event/edit_event.html'),
                          is_group_admin(v.edit_event_page)),
                   PUT=is_group_admin(v.edit_event))

event_popup_partial = route(GET=v.event_popup_partial)

event_registration = has_training(route(POST=v.register_for_event,
                                        DELETE=v.cancel_event_registration))

start_event_map_print_job = do(has_training,
                               route(POST=v.start_event_map_print_job))

event_check_in_page = do(is_group_admin,
                         route(GET=do(
                             render_template('event/admin_checkin.html'),
                             v.event_check_in_page)))

event_check_in = is_group_admin(route(POST=v.check_in_user_to_event,
                                      DELETE=v.un_check_in_user_to_event))

email_event_registered_users = do(is_group_admin,
                                  route(POST=v.email_event_registered_users))
