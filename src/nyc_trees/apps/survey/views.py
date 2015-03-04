# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import json

from django.conf import settings
from django.db import transaction
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from apps.core.models import Group
from apps.core.views import map_legend

from apps.event.models import Event
from apps.event.helpers import user_is_checked_in_to_event

from apps.users.models import TrustedMapper

from apps.survey.models import (BlockfaceReservation, Blockface, Territory,
                                Survey, Tree, Species, CURB_CHOICES,
                                STATUS_CHOICES, CERTAINTY_CHOICES,
                                HEALTH_CHOICES, STEWARDSHIP_CHOICES,
                                GUARD_CHOICES, SIDEWALK_CHOICES,
                                PROBLEMS_CHOICES)
from apps.survey.layer_context import (get_context_for_reservations_layer,
                                       get_context_for_reservable_layer,
                                       get_context_for_progress_layer,
                                       get_context_for_territory_survey_layer,
                                       get_context_for_territory_admin_layer)


def progress_page(request):
    context = map_legend(request)
    context['layer'] = get_context_for_progress_layer(request)
    return context


def progress_page_blockface_popup(request, blockface_id):
    survey_type = request.GET.get('survey_type')
    group_id = request.GET.get('group_id', None)
    group = get_object_or_404(Group, id=group_id) if group_id else None
    return {
        'survey_type': survey_type,
        'group': group
    }


def cancel_reservation(request, blockface_id):
    update_time = now()
    _query_reservation(request.user, blockface_id) \
        .update(canceled_at=update_time, updated_at=update_time)

    return get_context_for_reservations_layer(request)


def _query_reservation(user, blockface_id):
    return BlockfaceReservation.objects \
        .filter(blockface_id=blockface_id, user=user) \
        .current()


def blockface_cart_page(request):
    return {
        'blockface_ids': request.POST['ids']
    }


def reservations_page(request):
    return {
        'legend_entries': [
            {'css_class': 'reserved', 'label': 'Reserved by you'},
            {'css_class': 'unavailable', 'label': 'Not reserved by you'},
        ],
        'layer': get_context_for_reservations_layer(request),
        'bounds': _user_reservation_bounds(request.user)
    }


def _user_reservation_bounds(user):
    reservations = BlockfaceReservation.objects \
        .filter(user=user) \
        .current() \
        .values_list('blockface_id', flat=True)
    blockfaces = Blockface.objects.filter(id__in=reservations).collect()
    return list(blockfaces.extent) if blockfaces else None


def reserve_blockfaces_page(request):
    current_reservations_amount = BlockfaceReservation.objects \
        .filter(user=request.user) \
        .current() \
        .count()

    return {
        'reservations': {
            'current': 0,
            'total': settings.RESERVATIONS_LIMIT - current_reservations_amount
        },
        'layer': get_context_for_reservable_layer(request),
        'legend_entries': [
            {'css_class': 'available', 'label': 'Available'},
            {'css_class': 'unavailable', 'label': 'Unavailable'},
        ]
    }


def reserved_blockface_popup(request, blockface_id):
    blockface = get_object_or_404(Blockface, id=blockface_id)
    reservation = _query_reservation(request.user, blockface_id)[0]
    return {
        'blockface': blockface,
        'reservation': reservation
    }


@transaction.atomic
def confirm_blockface_reservations(request):
    id_string = request.POST['ids']
    ids = id_string.split(',')

    is_mapping_with_paper = request.POST['is_mapping_with_paper'] == 'True'

    blockfaces = Blockface.objects \
        .filter(id__in=ids) \
        .select_related('territory')

    user_trusted_group_ids = TrustedMapper.objects \
        .filter(user=request.user, is_approved=True) \
        .values_list('group_id', flat=True)

    user_admin_group_ids = Group.objects \
        .filter(admin=request.user) \
        .values_list('id', flat=True)

    already_reserved_blockface_ids = BlockfaceReservation.objects \
        .filter(blockface__id__in=ids) \
        .current() \
        .values_list('blockface_id', flat=True)

    expiration_date = now() + settings.RESERVATION_TIME_PERIOD
    reservations = []

    for blockface in blockfaces:
        territory = _get_territory(blockface)

        if ((blockface.is_available and
             blockface.id not in already_reserved_blockface_ids and
             (territory is None or
              territory.group_id in user_trusted_group_ids or
              territory.group_id in user_admin_group_ids))):
            reservations.append(BlockfaceReservation(
                blockface=blockface,
                user=request.user,
                is_mapping_with_paper=is_mapping_with_paper,
                expires_at=expiration_date
            ))

    BlockfaceReservation.objects.bulk_create(reservations)

    # TODO: Send email confirmation (Github issue #434)

    return {
        'blockfaces_requested': len(ids),
        'blockfaces_reserved': len(reservations),
        'expiration_date': expiration_date
    }


def _get_territory(blockface):
    try:
        return blockface.territory
    except Territory.DoesNotExist:
        return None


def blockface(request, blockface_id):
    blockface = get_object_or_404(Blockface, id=blockface_id)
    return {
        'id': blockface.id,
        'extent': blockface.geom.extent,
        'geojson': blockface.geom.geojson
    }


def start_survey(request):
    return {
        'layer': get_context_for_reservations_layer(request),
        'bounds': _user_reservation_bounds(request.user),
        'choices': _get_survey_choices()
    }


def start_survey_from_event(request, event_slug):
    group = request.group
    event = get_object_or_404(Event, group=group, slug=event_slug)
    if not event.in_progress():
        return HttpResponseForbidden('Event not currently in-progress')
    if not user_is_checked_in_to_event(request.user, event):
        return HttpResponseForbidden('User not checked-in to this event')

    return {
        'layer': get_context_for_territory_survey_layer(request, group.id),
        'location': [event.location.y, event.location.x],
        'choices': _get_survey_choices()
    }


def _get_survey_choices():
    # NOTE: "No Problems" is handled in the template
    grouped_problem_choices = [choice for choice in PROBLEMS_CHOICES
                               if isinstance(choice[1], tuple)]

    guard_installation_choices = (('Yes', 'Installed'),
                                  ('No', 'Not installed'))
    guard_helpfulness_choices = [choice for choice in GUARD_CHOICES
                                 if choice[0] != 'None']

    species_choices = Species.objects.all().values_list('pk', 'name')

    return {
        'curb_location': CURB_CHOICES,
        'status': STATUS_CHOICES,
        'species': species_choices,
        'species_certainty': CERTAINTY_CHOICES,
        'health': HEALTH_CHOICES,
        'stewardship': STEWARDSHIP_CHOICES,
        'guard_installation': guard_installation_choices,
        'guards': guard_helpfulness_choices,
        'sidewalk_damage': SIDEWALK_CHOICES,
        'problem_groups': grouped_problem_choices,
    }


def submit_survey(request):
    return _create_survey_and_trees(request)


def submit_survey_from_event(request, event_slug):
    event = get_object_or_404(Event, group=request.group, slug=event_slug)
    if not user_is_checked_in_to_event(request.user, event):
        return HttpResponseForbidden('User not checked-in to this event')

    return _create_survey_and_trees(request, event)


@transaction.atomic
def _create_survey_and_trees(request, event=None):
    """
    Creates survey and trees from JSON body, where k1... are model attrs: {
        survey: { k1:v1, ... },
        trees: [
            { k1:v1, ...},
            ...
        ]
    }
    trees.problems should be a list of problem codes -- ["Stones", "Sneakers"]
    """
    data = json.loads(request.body)
    survey_data = data['survey']
    tree_list = data.get('trees', [])

    survey = Survey(user=request.user, **survey_data)

    if survey.has_trees and len(tree_list) == 0:
        return HttpResponseBadRequest('Trees expected but absent')
    if not survey.has_trees and len(tree_list) > 0:
        return HttpResponseBadRequest('Trees not expected but present')

    blockface = survey.blockface

    if event:
        territory = _get_territory(blockface)
        if territory is None or territory.group_id != event.group_id:
            return HttpResponseForbidden(
                "Blockface is not in group's territory.")
    else:
        if not _query_reservation(request.user, blockface.id).exists():
            return HttpResponseForbidden(
                'You have not reserved this blockface.')

    survey.clean_and_save()

    if survey.quit_reason == '':
        blockface.is_available = False
        blockface.clean_and_save()

    for tree_data in tree_list:
        if 'problems' in tree_data:
            tree_data['problems'] = ','.join(tree_data['problems'])
        tree = Tree(survey=survey, **tree_data)
        tree.clean_and_save()

    return {'survey_id': survey.id}


def flag_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id, user=request.user)
    survey.is_flagged = True
    survey.clean_and_save()
    return {'success': True}


def species_autocomplete_list(request):
    # TODO: implement
    pass


def admin_territory_page(request):
    context = {
        'groups': Group.objects.all(),
        'legend_entries': [
            {'css_class': 'available', 'label': 'Available'},
            {'css_class': 'reserved', 'label': "This group's territory"},
            {'css_class': 'unavailable',
             'label': "Others' territory/reservations"},
            {'css_class': 'surveyed-by-me', 'label': 'Mapped by this group'},
            {'css_class': 'surveyed-by-others', 'label': 'Mapped by others'},
        ]
    }
    context['layer'] = get_context_for_territory_admin_layer(request)
    return context


def admin_blockface_page(request):
    # TODO: implement
    pass


def admin_blockface_partial(request):
    # TODO: implement
    pass


def admin_blockface_detail_page(request, blockface_id):
    # TODO: implement
    pass


def admin_extend_blockface_reservation(request, blockface_id):
    # TODO: implement
    pass


def admin_blockface_available(request, blockface_id):
    # TODO: implement
    pass


def reservations_instructions(request):
    pass
