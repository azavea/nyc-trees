# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from apps.core.models import User
from apps.users import can_show_full_name


def teammates_for_event(group, event, current_user):
    attendees = User.objects.exclude(id=current_user.id)\
                            .filter(eventregistration__event=event,
                                    eventregistration__did_attend=True)\
                            .order_by('username')
    return _teammates_context(attendees)


def teammates_for_individual_mapping(current_user):
    mappers = User.objects.exclude(id=current_user.id)\
                          .filter(individual_mapper=True)
    return _teammates_context(mappers)


def _teammates_context(users):
    return [_teammate_user_context(u) for u in users]


def _teammate_user_context(user):
    if can_show_full_name(user):
        full_name = ("%s %s" % (user.first_name, user.last_name)).strip()
    else:
        full_name = ""
    return {
        "user_id": user.id,
        "username": user.username,
        "full_name": full_name
    }
