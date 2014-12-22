# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.auth.decorators import login_required

from django_tinsel.decorators import route, render_template
from django_tinsel.utils import decorate as do

from apps.core.decorators import is_group_admin

from apps.users.views import group as v

group_list_page = route(GET=do(render_template('groups/list.html'),
                               v.group_list_page))

group_detail = route(GET=do(render_template('groups/detail.html'),
                            v.group_detail))

group_edit = do(is_group_admin,
                render_template('groups/settings.html'),
                route(GET=v.edit_group,
                      POST=v.update_group_settings))

follow_group = login_required(route(POST=v.follow_group))

unfollow_group = login_required(route(POST=v.unfollow_group))

# TODO: should this have group_admin
start_group_map_print_job = route(POST=v.start_group_map_print_job)

edit_user_mapping_priveleges = do(
    is_group_admin,
    route(PUT=v.give_user_mapping_priveleges,
          DELETE=v.remove_user_mapping_priveleges))
