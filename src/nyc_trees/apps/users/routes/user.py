# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.auth.decorators import login_required

from django_tinsel.decorators import route, render_template
from django_tinsel.utils import decorate as do

from apps.users.views import user as v

render_user_template = render_template('users/profile.html')
render_settings_template = render_template('users/settings.html')

user_detail_redirect = do(login_required,
                          route(GET=v.user_detail_redirect))

user_profile_settings = do(
    login_required,
    render_settings_template,
    route(GET=v.profile_settings,
          POST=v.update_profile_settings))

achievements = do(login_required,
                  route(GET=do(render_template('users/achievement.html'),
                               v.achievements_page)))

user_detail = route(
    GET=do(render_user_template, v.user_detail),
    POST=do(login_required, render_user_template, v.set_privacy))

request_individual_mapper_status = do(
    login_required,
    route(POST=v.request_individual_mapper_status))

start_form_for_reservation_job = route(POST=v.start_form_for_reservation_job)
start_map_for_reservation_job = route(POST=v.start_map_for_reservation_job)
start_map_for_tool_depots_job = route(POST=v.start_map_for_tool_depots_job)
