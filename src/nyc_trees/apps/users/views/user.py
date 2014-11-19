# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.http import Http404
from django.shortcuts import get_object_or_404

from apps.core.decorators import decorate as do, render_template
from apps.core.models import User


def user_profile_context(request, username):
    user = get_object_or_404(User, username=username)
    its_me = (user.id == request.user.id)

    if not its_me and not user.profile_is_public:
        # Private profile acts like a missing page to others
        raise Http404()

    return {
        'user': user,
        'viewing_own_profile': its_me,
        'show_username': ((its_me or user.real_name_is_public) and
                          (user.first_name or user.last_name)),
        'show_achievements': its_me or user.achievements_are_public,
        'show_contributions': its_me or user.contributions_are_public,
        'show_groups': its_me or user.group_follows_are_public,
        'show_individual_mapper': (user.individual_mapper and
                                   (its_me or user.profile_is_public))
    }


def update_user(request, username):
    # TODO: implement
    pass


def request_individual_mapper_status(request, username):
    # TODO: implement
    pass


def start_form_for_reservation_job(request, username):
    # TODO: implement
    pass


def start_map_for_reservation_job(request, username):
    # TODO: implement
    pass


def start_map_for_tool_depots_job(request, username):
    # TODO: implement
    pass


user_detail = do(
    render_template('users/profile.html'),
    user_profile_context)
