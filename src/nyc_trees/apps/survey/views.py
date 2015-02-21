# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf import settings
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from apps.core.models import Group
from apps.core.views import map_legend

from apps.event.models import Event
from apps.event.helpers import user_is_checked_in_to_event

from apps.users.models import TrustedMapper

from apps.survey.models import BlockfaceReservation, Blockface, Territory
from apps.survey.layer_context import (get_context_for_reservations_layer,
                                       get_context_for_reservable_layer,
                                       get_context_for_progress_layer,
                                       get_context_for_territory_survey_layer)


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
    BlockfaceReservation.objects \
        .filter(blockface_id=blockface_id) \
        .filter(user=request.user) \
        .current() \
        .update(canceled_at=update_time, updated_at=update_time)

    return get_context_for_reservations_layer(request)


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
        'layer': get_context_for_reservations_layer(request)
    }


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
    reservation = BlockfaceReservation.objects \
        .filter(blockface=blockface) \
        .filter(user=request.user) \
        .current()[0]

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

    already_reserved_blockface_ids = BlockfaceReservation.objects \
        .filter(blockface__id__in=ids) \
        .current() \
        .values_list('blockface_id', flat=True)

    expiration_date = now() + settings.RESERVATION_TIME_PERIOD
    reservations = []

    for blockface in blockfaces:
        try:
            territory = blockface.territory
        except Territory.DoesNotExist:
            territory = None

        if ((blockface.is_available and
             blockface.id not in already_reserved_blockface_ids and
             (territory is None or
              territory.group_id in user_trusted_group_ids))):
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


def blockface(request, blockface_id):
    return {'extent': Blockface.objects.get(pk=blockface_id).geom.extent}


def start_survey(request):
    # TODO: Set bounds to reservations extent
    return {
        'layer': get_context_for_reservations_layer(request),
        'legend_entries': [
        ]
    }


def start_survey_from_event(request, event_slug):
    # TODO pull blockface from querystring/hash
    # Set bounds to event location
    group = request.group
    event = get_object_or_404(Event, group=request.group, slug=event_slug)
    if not event.in_progress():
        return HttpResponseForbidden('Event not currently in-progress')
    if not user_is_checked_in_to_event(request.user, event):
        return HttpResponseForbidden('User not checked-in to this event')
    return {
        'map_location': [event.location.y, event.location.x],
        'layer': get_context_for_territory_survey_layer(request, group.id),
        'legend_entries': [
        ]
    }


def submit_survey(request, blockface_id):
    # TODO: implement
    pass


def species_autocomplete_list(request):
    # TODO: implement
    pass


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
