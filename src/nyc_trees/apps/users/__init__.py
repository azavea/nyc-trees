# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.core.urlresolvers import reverse

from libs.sql import get_user_tree_count, get_user_surveyed_species
from apps.users.forms import PrivacySettingsForm
from apps.users.models import achievements


_FOLLOWED_GROUP_CHUNK_SIZE = 2
_RESERVATION_CHUNK_SIZE = 2


def user_profile_context(user, its_me=True, home_page=True):
    user_achievements = set(user.achievement_set
                            .order_by('created_at')
                            .values_list('achievement_id', flat=True))

    block_count = user.survey_set.distinct('blockface').count()
    tree_count = get_user_tree_count(user)
    species_surveyed = get_user_surveyed_species(user)
    # Distinct count, not total
    species_count = len(species_surveyed)
    event_count = user.eventregistration_set \
        .filter(did_attend=True) \
        .count()

    # In order to show the tree count in a "ticker" we need to break it up
    # into digits and pad it with zeroes.
    tree_digits = [digit for digit in "{:07d}".format(tree_count)]

    privacy_form = PrivacySettingsForm(instance=user)

    contributions_title = 'Your Contributions' if its_me else 'Contributions'

    context = {
        'user': user,
        'viewing_own_profile': its_me,
        'show_username': can_show_full_name(user, its_me),
        'show_achievements': its_me or user.achievements_are_public,
        'show_contributions': (not home_page and
                               (its_me or user.contributions_are_public)),
        'contributions_title': contributions_title,
        'show_groups': its_me or user.group_follows_are_public,
        'show_individual_mapper': (user.individual_mapper and
                                   (its_me or user.profile_is_public)),
        'show_reservations': (user.individual_mapper and its_me),
        'show_request_access': (its_me and
                                user.eligible_to_become_individual_mapper()),
        'follows': _get_follows_context(user),
        'reservations': _get_reservations_context(user),
        'privacy_categories': get_privacy_categories(privacy_form),
        'counts': {
            'block': block_count,
            'tree': tree_count,
            'tree_digits': tree_digits,
            'species': species_count,
            'species_by_name': species_surveyed,
            'event': event_count
        },
        'achievements': [achievements[key]
                         for key in user_achievements if key in achievements]
    }
    return context


def can_show_full_name(user, its_me=False):
    return ((its_me or user.real_name_is_public) and
            (user.first_name or user.last_name))


def get_privacy_categories(form):
    user = form.instance

    def make_category(title, field_name):
        return {
            'title': title,
            'field_name': field_name,
            'is_public': getattr(user, field_name),
            'form_field': form[field_name]
        }

    return [
        make_category('Profile', 'profile_is_public'),
        make_category('Name', 'real_name_is_public'),
        make_category('Groups', 'group_follows_are_public'),
        make_category('Contributions', 'contributions_are_public'),
        make_category('Achievements', 'achievements_are_public'),
    ]


def _get_list_section_context(key, qs, chunk_size):
    count = qs.count()
    hidden_count = count - chunk_size

    return {
        'count': count,
        'chunk_size': chunk_size,
        'hidden_count': hidden_count,
        key: qs
    }


def _get_follows_context(user):
    follows = user.follow_set.select_related('group').order_by('created_at')
    return _get_list_section_context('follows', follows,
                                     _FOLLOWED_GROUP_CHUNK_SIZE)


def _get_reservations_context(user):
    reservations = user.blockfacereservation_set\
                       .current()\
                       .select_related('blockface')\
                       .order_by('expires_at')
    context = _get_list_section_context('reservations', reservations,
                                        _RESERVATION_CHUNK_SIZE)

    context['map_poll_url'] = reverse('reservations_map_pdf_poll')
    return context
