# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from apps.users.models import TrustedMapper


def user_is_census_admin(user):
    return user.is_authenticated() and user.is_superuser


def user_is_group_admin(user, group):
    return user.is_authenticated() and (user.is_superuser or
                                        group.admin == user)


def user_has_online_training(user):
    return user.is_authenticated() and user.online_training_complete


def user_has_field_training(user):
    return user.is_authenticated() and user.field_training_complete


def user_is_individual_mapper(user):
    return user.is_authenticated() and user.individual_mapper


def user_is_trusted_mapper(user, group):
    return user.is_authenticated() and \
        TrustedMapper.objects.filter(group=group,
                                     user=user,
                                     is_approved=True).exists()


def user_is_eligible_to_become_trusted_mapper(user, group):
    return user.is_authenticated() and \
        user.eligible_to_become_trusted_mapper(group)
