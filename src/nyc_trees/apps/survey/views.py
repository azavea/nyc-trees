# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import os
import json
import shortuuid
from pytz import timezone

from celery import chain

from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.urlresolvers import reverse
from django.db import transaction, connection
from django.db.models import Q
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseBadRequest)
from django.shortcuts import get_object_or_404, redirect
from django.utils.timezone import now
from django.utils.html import escape

from apps.core.models import User, Group
from apps.core.helpers import (user_is_group_admin, user_is_individual_mapper,
                               user_is_census_admin)

from apps.event.models import Event
from apps.event.helpers import (user_is_checked_in_to_event,
                                user_is_rsvped_for_event)

from apps.mail.tasks import notify_reservation_confirmed
from libs.pdf_maps import create_reservations_map_pdf

from apps.users import can_show_full_name
from apps.users.models import TrustedMapper
from apps.survey.models import (BlockfaceReservation, Blockface, Territory,
                                Survey, Tree, Species, CURB_CHOICES,
                                STATUS_CHOICES, CERTAINTY_CHOICES,
                                HEALTH_CHOICES, STEWARDSHIP_CHOICES,
                                GUARD_CHOICES, SIDEWALK_CHOICES,
                                PROBLEMS_CHOICES)
from apps.survey.layer_context import (
    get_context_for_reservations_layer, get_context_for_reservable_layer,
    get_context_for_progress_layer, get_context_for_territory_survey_layer,
    get_context_for_printable_reservations_layer,
    get_context_for_group_progress_layer, get_context_for_user_progress_layer,
    get_context_for_borough_progress_layer, get_context_for_nta_progress_layer
)
from apps.survey.helpers import group_percent_completed

from libs.pdf_maps import create_and_save_pdf


_SURVEY_DETAIL_QUERY_FILE = os.path.join(os.path.dirname(__file__),
                                         'survey_detail.sql')

with open(_SURVEY_DETAIL_QUERY_FILE, 'r') as f:
    _SURVEY_DETAIL_QUERY = f.read()


def progress_page(request):
    context = {
        'legend_entries': [
            {'mode': 'all', 'css_class': 'mapped', 'label': 'Mapped'},
            {'mode': 'all', 'css_class': 'not-mapped', 'label': 'Not mapped'},

            {'mode': 'my', 'css_class': 'mapped', 'label': 'Mapped by you'},
            {'mode': 'my', 'css_class': 'not-mapped',
             'label': 'Not mapped by you'},

            {'mode': 'group', 'css_class': 'mapped',
             'label': 'Mapped by this group'},
            {'mode': 'group', 'css_class': 'not-mapped',
             'label': 'Not mapped'},
        ],
        'percentage_ramps': range(0, 100, 10),
        'legend_mode': 'all-percent',
        'layer_all': get_context_for_progress_layer(),
        'layer_all_nta': get_context_for_nta_progress_layer(),
        'layer_all_borough': get_context_for_borough_progress_layer(),
        'help_shown': _was_help_shown(request, 'progress_page_help_shown')
    }

    user = request.user
    if user.is_authenticated():
        context['layer_my'] = get_context_for_user_progress_layer(request)

        blocks = (user.surveys.distinct('blockface')
                  .values_list('blockface_id', flat=True))
        if len(blocks) > 0:
            blockfaces = Blockface.objects.filter(id__in=blocks).collect()
            context['my_bounds'] = list(blockfaces.extent)

    return context


def _was_help_shown(request, help_shown_attr):
    """
    help_shown_attr is a user attribute specifying whether help has been
    shown on a particular page. We also use it as a session attribute
    for non-logged-in users.

    Calling this function returns the current attribute value, and also
    sets it to True (so it will only be shown once).
    """
    help_shown = request.session.get(help_shown_attr, False)
    request.session[help_shown_attr] = True

    user = request.user
    if user.is_authenticated():
        user_help_shown = getattr(user, help_shown_attr)
        help_shown = help_shown or user_help_shown

        if not user_help_shown:
            setattr(user, help_shown_attr, True)
            user.save()

    return help_shown


def progress_page_blockface_popup(request, blockface_id):
    blockface = get_object_or_404(Blockface, id=blockface_id)

    turf = Territory.objects.filter(blockface_id=blockface_id)
    groups = Group.objects.filter(pk=turf.values_list('group_id', flat=True))
    group = groups[0] if len(groups) else None

    is_active = (group is None or group.is_active or
                 user_is_group_admin(request.user, group))

    survey_type = _get_survey_type(blockface, request.user, group)

    return {
        'survey_type': survey_type,
        'group': group,
        'is_active': is_active
    }


def _get_survey_type(blockface, user, group):
    if user.is_authenticated():
        reserved_by_user = BlockfaceReservation.objects \
            .filter(blockface=blockface, user=user).current().exists()

        if reserved_by_user:
            return 'reserved'

    try:
        latest_survey = Survey.objects \
            .filter(blockface=blockface) \
            .latest('created_at')

        if user.is_authenticated() and user.pk in {
           latest_survey.user_id, latest_survey.teammate_id}:
            return 'surveyed-by-me'
        else:
            return 'surveyed-by-others'
    except Survey.DoesNotExist:
        pass

    if group is None and blockface.is_available:
        return 'available'

    return 'unavailable'


def _query_reservation(user, blockface_id):
    return BlockfaceReservation.objects \
        .filter(blockface_id=blockface_id, user=user) \
        .current()


def blockface_cart_page(request):
    ids_str = request.POST.get('ids', None)
    ids = ids_str.split(',') if ids_str else []
    cancelled_reservations = _get_reservations_to_cancel(ids, request.user)
    already_reserved_ids = _already_reserved_blockface_ids(ids)

    return {
        'blockface_ids': request.POST['ids'],
        'num_reserved': len(ids) - already_reserved_ids.count(),
        'num_cancelled': cancelled_reservations.count()
    }


def user_reserved_blockfaces_geojson(request):
    reservations = BlockfaceReservation.objects \
        .select_related('blockface') \
        .filter(user=request.user) \
        .current()

    est_tz = timezone('US/Eastern')

    def get_formatted_expiration_date(reservation):
        dt = reservation.expires_at.astimezone(est_tz)
        return dt.strftime('%b %-d, %Y')

    return [
        {
            'type': 'Feature',
            'geometry': {
                'type': 'MultiLineString',
                'coordinates': reservation.blockface.geom.coords
            },
            'properties': {
                'id': reservation.blockface.id,
                'expires_at': get_formatted_expiration_date(reservation)
            }
        }
        for reservation in reservations
    ]


def group_borders_geojson(request):
    groups = Group.objects.filter(is_active=True)

    base_group_layer_context = get_context_for_group_progress_layer()
    base_group_tile_url = base_group_layer_context['tile_url']
    base_group_grid_url = base_group_layer_context['grid_url']

    return [
        {
            'type': 'Feature',
            'geometry': {
                'type': 'MultiPolygon',
                'coordinates': list(group.border.coords)
            },
            'properties': {
                'tileUrl': '%s?group=%s' % (base_group_tile_url, group.id),
                'gridUrl': '%s?group=%s' % (base_group_grid_url, group.id),
                'popupUrl': reverse('group_popup',
                                    kwargs={'group_slug': group.slug}),
                'bounds': group.border.extent
            }
        }
        for group in groups
        if group.border
    ]


def group_popup(request):
    return {
        'group': request.group,
        'completed': group_percent_completed(request.group)
    }


def reservations_map_pdf_poll(request):
    # Update reservations map PDF if reservations have changed
    user = request.user
    reservation_ids = _reservation_ids(user)
    if reservation_ids != user.reservation_ids_in_map_pdf:
        create_reservations_map_pdf(request, reservation_ids)

    url = request.user.reservations_map_pdf_url
    if url:
        return {'map_pdf_url': url}
    else:
        return {}


def _reservation_ids(user):
    reservation_ids = BlockfaceReservation.objects \
        .filter(user=user) \
        .current() \
        .order_by('id') \
        .values_list('id', flat=True)
    reservation_ids = ','.join(str(x) for x in reservation_ids)
    return reservation_ids


def printable_reservations_page(request):
    blockfaces = _user_reservations(request.user)

    endpoints = set()
    for blockface in blockfaces:
        coords = blockface.geom.coords[0]
        endpoints.add(coords[0])
        endpoints.add(coords[-1])
    # make list of [lat,lng] coordinates for leaflet convenience
    endpoints = [[e[1], e[0]] for e in endpoints]

    return {
        'layer': get_context_for_printable_reservations_layer(request),
        'bounds': list(blockfaces.collect().extent) if blockfaces else None,
        'endpoints': endpoints
    }


def _user_reservation_bounds(user):
    blockfaces = _user_reservations(user)
    return list(blockfaces.collect().extent) if blockfaces else None


def _user_reservations(user):
    reservations = BlockfaceReservation.objects \
        .filter(user=user) \
        .current() \
        .values_list('blockface_id', flat=True)
    blockfaces = Blockface.objects.filter(id__in=reservations)
    return blockfaces


def reserve_blockfaces_page(request):
    if not user_is_individual_mapper(request.user):
        return redirect('reservations_instructions')

    current_reservations_amount = BlockfaceReservation.objects \
        .filter(user=request.user) \
        .current() \
        .count()

    return {
        'reservations': {
            'current': current_reservations_amount,
            'total': settings.RESERVATIONS_LIMIT
        },
        'layer': get_context_for_reservable_layer(request),
        'bounds': _user_reservation_bounds(request.user),
        'legend_entries': [
            {'css_class': 'available', 'label': 'Available'},
            {'css_class': 'unavailable', 'label': 'Unavailable'},
            {'css_class': 'reserved', 'label': 'Reserved by you'},
            {'css_class': 'in-cart', 'label': 'In your cart'},
        ],
        'help_shown': _was_help_shown(request, 'reservations_page_help_shown')
    }


@transaction.atomic
def confirm_blockface_reservations(request):
    id_string = request.POST['ids']
    ids = id_string.split(',')
    # Filter empty strings
    ids = filter(None, ids)

    is_mapping_with_paper = \
        request.POST.get('is_mapping_with_paper', 'False') == 'True'

    blockfaces = Blockface.objects \
        .filter(id__in=ids) \
        .select_related('territory')

    user_trusted_group_ids = TrustedMapper.objects \
        .filter(user=request.user, is_approved=True) \
        .values_list('group_id', flat=True)

    user_admin_group_ids = Group.objects \
        .filter(admin=request.user) \
        .values_list('id', flat=True)

    already_reserved_blockface_ids = _already_reserved_blockface_ids(ids)

    right_now = now()
    expiration_date = right_now + settings.RESERVATION_TIME_PERIOD

    new_reservations = []

    for blockface in blockfaces:
        territory = _get_territory(blockface)

        if ((blockface.is_available and
             blockface.id not in already_reserved_blockface_ids and
             (territory is None or user_is_census_admin(request.user) or
              territory.group_id in user_trusted_group_ids or
              territory.group_id in user_admin_group_ids))):
            new_reservations.append(BlockfaceReservation(
                blockface=blockface,
                user=request.user,
                is_mapping_with_paper=is_mapping_with_paper,
                expires_at=expiration_date
            ))

    cancelled_reservations = _get_reservations_to_cancel(ids, request.user)
    num_cancelled = cancelled_reservations.count()

    cancelled_reservations.update(canceled_at=right_now, updated_at=right_now)

    # Workaround for Django limitation which prevents us from obtaining
    # primary keys for objects created in bulk.
    for reservation in new_reservations:
        reservation.save()

    reservation_ids = [r.id for r in new_reservations]

    filename = "reservations_map/%s_%s.pdf" % (
        request.user.username, shortuuid.uuid())
    request.user.reservations_map_pdf_filename = filename
    request.user.clean_and_save()

    url = reverse('printable_reservations_map')
    host = request.get_host()

    if hasattr(request, 'session'):  # prevent test failure
        session_id = request.session.session_key
        chain(create_and_save_pdf.s(session_id, host, url, filename),
              notify_reservation_confirmed.s(request.user.id,
                                             reservation_ids)) \
            .apply_async()

    num_reserved = len(new_reservations)
    return {
        'n_requested': len(ids) - len(already_reserved_blockface_ids),
        'n_reserved': num_reserved,
        'n_cancelled': num_cancelled,
        'expiration_date': expiration_date
    }


def _get_territory(blockface):
    try:
        return blockface.territory
    except Territory.DoesNotExist:
        return None


def _already_reserved_blockface_ids(ids):
    return BlockfaceReservation.objects \
        .filter(blockface__id__in=ids) \
        .current() \
        .values_list('blockface_id', flat=True)


def _get_reservations_to_cancel(ids, user):
    # Whatever blockface IDs were not submitted, should be cancelled
    return BlockfaceReservation.objects \
        .filter(user=user) \
        .exclude(blockface__id__in=ids) \
        .current()


def _blockface_context(blockface):
    return {
        'id': blockface.id,
        'extent': blockface.geom.extent,
        'geojson': blockface.geom.geojson
    }


def blockface(request, blockface_id):
    blockface = get_object_or_404(Blockface, id=blockface_id)
    return _blockface_context(blockface)


def blockface_near_point(request):
    p = Point(float(request.GET.get('lng', 0)),
              float(request.GET.get('lat', 0)),
              srid=4326)

    # The size of the distance filter was chosen through trial and
    # error by testing tap precision on a mobile device
    qs = Blockface.objects.filter(geom__dwithin=(p, 0.0002))\
                          .distance(p)\
                          .order_by('distance')
    blockfaces = qs[:1]  # We only want the closest blockface
    if blockfaces:
        return _blockface_context(blockfaces[0])
    else:
        return {
            'error': 'Block edge not found near lat:%f lon:%f' % (p.y, p.x)
        }


def _validate_event_and_group(request, event_slug):
    event = get_object_or_404(Event, group=request.group, slug=event_slug)
    if not user_is_checked_in_to_event(request.user, event):
        raise PermissionDenied('User not checked-in to this event')
    return event


def start_survey(request):
    reservations_for_user = (
        BlockfaceReservation.objects.remaining_for(request.user))
    return {
        'layer': get_context_for_reservations_layer(request),
        'bounds': _user_reservation_bounds(request.user),
        'choices': _get_survey_choices(),
        'no_more_reservations': reservations_for_user <= 1,
        'geolocate_help_shown': _was_help_shown(request,
                                                'survey_geolocate_help_shown'),
    }


def start_survey_from_event(request, event_slug):
    group = request.group
    event = get_object_or_404(Event, group=request.group, slug=event_slug)

    if not user_is_rsvped_for_event(request.user, event):
        raise PermissionDenied('User not checked-in to this event')

    if not user_is_checked_in_to_event(request.user, event):
        return redirect('event_user_check_in_page',
                        group_slug=event.group.slug, event_slug=event.slug)

    if not event.is_mapping_allowed():
        return HttpResponseForbidden('Event not currently in-progress')

    return {
        'layer': get_context_for_territory_survey_layer(group.id),
        'location': [event.location.y, event.location.x],
        'choices': _get_survey_choices(),
        'geolocate_help_shown': _was_help_shown(request,
                                                'survey_geolocate_help_shown'),
    }


def teammates_for_mapping(request):
    query = request.GET.get('q', None)

    users = User.objects.exclude(id=request.user.id) \
                        .filter(is_active=True) \
                        .order_by('username')

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            (Q(real_name_is_public=True) & (Q(first_name__icontains=query) |
                                            Q(last_name__icontains=query))))

    return [_teammate_user_context(u) for u in users]


def _teammate_user_context(user):
    if can_show_full_name(user):
        text = "{} — {} {}".format(
            escape(user.username), escape(user.first_name),
            escape(user.last_name))
    else:
        text = user.username

    return {
        "id": user.id,
        "text": text.strip()
    }


def _get_survey_choices():
    # NOTE: "No Problems" is handled in the template
    grouped_problem_choices = [choice for choice in PROBLEMS_CHOICES
                               if isinstance(choice[1], tuple)]

    guard_installation_choices = (('No', 'Not installed'),
                                  ('Yes', 'Installed'))
    guard_helpfulness_choices = [choice for choice in GUARD_CHOICES
                                 if choice[0] != 'None']

    species_choices = Species.objects.all()

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
    ctx = {}

    # sometimes a dict, sometimes HttpResponse
    create_result = _create_survey_and_trees(request)

    if isinstance(create_result, HttpResponse):
        return create_result
    else:
        ctx.update(create_result)
        return ctx


def submit_survey_from_event(request, event_slug):
    event = _validate_event_and_group(request, event_slug)
    return _create_survey_and_trees(request, event)


def _mark_survey_blockface_availability(survey, availability):
    if not isinstance(availability, bool):
        raise ValidationError('availability arg must be a boolean value')

    survey.blockface.is_available = availability
    survey.blockface.full_clean()
    survey.blockface.save()


def restart_blockface(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id, user=request.user)
    _mark_survey_blockface_availability(survey, True)
    expiration_date = now() + settings.RESERVATION_TIME_PERIOD
    BlockfaceReservation.objects.create(blockface=survey.blockface,
                                        user=request.user,
                                        expires_at=expiration_date)
    return {'success': True}


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
                'You have not reserved this block edge.')

    survey.full_clean()
    survey.save()

    _mark_survey_blockface_availability(survey, False)

    for tree_data in tree_list:
        if 'problems' in tree_data:
            tree_data['problems'] = ','.join(tree_data['problems'])

        # Convert any floats into integers for all the integer fields in Tree
        for field in ('circumference', 'stump_diameter'):
            if field in tree_data:
                tree_data[field] = int(round(float(tree_data[field])))

        tree = Tree(survey=survey, **tree_data)
        tree.clean_and_save()

    return {'survey_id': survey.id}


def flag_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id, user=request.user)
    survey.is_flagged = True
    survey.full_clean()
    survey.save()
    ctx = {'success': True}
    return ctx


def _survey_detail(request, survey_id):
    survey = Survey.objects.get(id=survey_id)
    with connection.cursor() as cursor:
        cursor.execute(_SURVEY_DETAIL_QUERY, [survey_id])
        trees = [tree[0] for tree in cursor]
    return {
        'survey_id': survey_id,
        'blockface_id': survey.blockface_id,
        'trees': json.dumps(trees),
        'bounds': list(survey.blockface.geom.extent),
    }


def survey_detail_from_event(request, event_slug, survey_id):
    _validate_event_and_group(request, event_slug)
    return _survey_detail(request, survey_id)


def survey_detail(request, survey_id):
    ctx = _survey_detail(request, survey_id)
    reservations_for_user = (
        BlockfaceReservation.objects.remaining_for(request.user))
    ctx.update({'no_more_reservations': reservations_for_user == 0})
    return ctx


def admin_territory_page(request):
    groups = Group.objects.all().order_by('name')
    context = {
        'groups': groups,
        'legend_entries': [
            {'css_class': 'available', 'label': 'Available'},
            {'css_class': 'reserved',
             'label': "This group's unmapped territory"},
            {'css_class': 'unavailable',
             'label': "Others' unmapped territory/reservations"},
            {'css_class': 'surveyed-by-me', 'label': 'Mapped by this group'},
            {'css_class': 'surveyed-by-others', 'label': 'Mapped by others'},
            {'css_class': 'selected',
             'label': 'Currently-selected block edges'},
        ]
    }
    return context


def reservations_instructions(request):
    user = request.user
    step1_complete = user.online_training_complete
    step2_complete = step1_complete and user.field_training_complete
    step3_complete = step2_complete and user.attended_at_least_two_events
    step4_complete = step3_complete and user.individual_mapper is not None
    return {
        'step1_complete': step1_complete,
        'step2_complete': step2_complete,
        'step3_complete': step3_complete,
        'step4_complete': step4_complete,
    }
