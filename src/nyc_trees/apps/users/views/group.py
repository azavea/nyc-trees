# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import json

from django.conf import settings
from django.contrib.gis.geos import Polygon
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from libs.data import merge
from libs.formatters import humanize_bytes
from libs.pdf_maps import create_event_map_pdf
from libs.sql import get_group_tree_count

from apps.core.helpers import (user_is_group_admin,
                               user_is_eligible_to_become_trusted_mapper)
from apps.core.decorators import group_request
from apps.core.models import Group

from apps.mail.views import notify_group_mapping_approved

from apps.users.models import Follow, TrustedMapper
from apps.users.forms import GroupSettingsForm

from apps.survey.models import Territory, Survey, Blockface
from apps.survey.layer_context import (get_context_for_territory_layer,
                                       get_context_for_territory_admin_layer)

from apps.event.models import Event, EventRegistration
from apps.event.event_list import EventList

GROUP_EVENTS_ID = 'group-events'
GROUP_EDIT_EVENTS_TAB_ID = 'events'


def group_list_page(request):
    # TODO: pagination
    groups = Group.objects.filter(is_active=True).order_by('name')
    group_ids = Follow.objects.filter(user_id=request.user.id) \
        .values_list('group_id', flat=True)
    user_is_following = [group.id in group_ids for group in groups]

    group_infos = zip(groups, user_is_following)
    return {
        'groups': group_infos,
        'groups_count': len(group_infos),
    }


@group_request
def _group_events(request):
    qs = Event.objects.filter(group=request.group, is_private=False)
    user_can_edit_group = user_is_group_admin(request.user,
                                              request.group)
    extra_context = {'user_can_edit_group': user_can_edit_group,
                     'group_slug': request.group.slug}
    return qs, extra_context


group_detail_events = EventList(
    _group_events,
    name="group_detail_events",
    template_path='groups/partials/detail_event_list.html')


group_edit_events = EventList(
    _group_events,
    name="group_edit_events",
    template_path='groups/partials/edit_event_list.html')


def group_detail(request):
    user = request.user
    group = request.group

    if not user_is_group_admin(user, group) and not request.group.is_active:
        raise Http404('Must be a group admin to view an inactive group')

    event_list = (group_detail_events
                  .configure(chunk_size=2,
                             active_filter=EventList.Filters.CURRENT,
                             filterset_name=EventList.chronoFilters)
                  .as_context(request, group_slug=group.slug))
    user_is_following = Follow.objects.filter(user_id=request.user.id,
                                              group=group).exists()

    show_mapper_request = user_is_eligible_to_become_trusted_mapper(user,
                                                                    group)

    follow_count = Follow.objects.filter(group=group).count()
    tree_count = get_group_tree_count(group)

    group_blocks = Territory.objects \
        .filter(group=group) \
        .values_list('blockface_id', flat=True)

    group_blocks_count = group_blocks.count()

    if group_blocks_count > 0:
        completed_blocks = Survey.objects \
            .filter(blockface_id__in=group_blocks) \
            .distinct('blockface')
        block_percent = "{:.1%}".format(
            float(completed_blocks.count()) / float(group_blocks.count()))
    else:
        block_percent = "0.0%"

    events_held = Event.objects.filter(group=group, ends_at__lt=now())
    num_events_held = events_held.count()

    num_event_attendees = EventRegistration.objects \
        .filter(event__in=events_held) \
        .filter(did_attend=True) \
        .count()

    return {
        'group': group,
        'event_list': event_list,
        'user_is_following': user_is_following,
        'edit_url': reverse('group_edit', kwargs={'group_slug': group.slug}),
        'show_mapper_request': show_mapper_request,
        'counts': {
            'tree': tree_count,
            'block': block_percent,
            'event': num_events_held,
            'attendees': num_event_attendees,
            'follows': follow_count
        },
        'group_events_id': GROUP_EVENTS_ID,
        'layer': get_context_for_territory_layer(request, request.group.id),
        'territory_bounds': _group_territory_bounds(request.group),
        'render_follow_button_without_count': request.POST.get(
            'render_follow_button_without_count', False)
    }


def redirect_to_group_detail(request):
    return HttpResponseRedirect(
        reverse('group_detail', kwargs={
            'group_slug': request.group.slug
        }))


def _group_territory_bounds(group):
    blockfaces = Blockface.objects \
        .filter(territory__group=group) \
        .collect()

    if blockfaces:
        return list(blockfaces.extent)
    else:
        return None


def edit_group(request, form=None):
    group = request.group
    if not form:
        form = GroupSettingsForm(instance=request.group, label_suffix='')
    event_list = (group_edit_events
                  .configure(chunk_size=2,
                             active_filter=EventList.Filters.CURRENT,
                             filterset_name=EventList.chronoFilters)
                  .as_context(request, group_slug=group.slug))
    pending_mappers = TrustedMapper.objects.filter(group=request.group,
                                                   is_approved__isnull=True)
    all_mappers = TrustedMapper.objects.filter(group=request.group,
                                               is_approved__isnull=False)
    return {
        'group': group,
        'event_list': event_list,
        'form': form,
        'group_slug': group.slug,
        'max_image_size': humanize_bytes(
            settings.MAX_GROUP_IMAGE_SIZE_IN_BYTES, 0),
        'pending_mappers': pending_mappers,
        'all_mappers': all_mappers,
        'group_edit_events_tab_id': GROUP_EDIT_EVENTS_TAB_ID,
    }


def update_group_settings(request):
    form = GroupSettingsForm(request.POST, request.FILES,
                             instance=request.group)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(request.group.get_absolute_url())
    else:
        return edit_group(request, form=form)


def follow_group(request):
    Follow.objects.get_or_create(user_id=request.user.id, group=request.group)
    return group_detail(request)


def unfollow_group(request):
    Follow.objects.filter(user_id=request.user.id, group=request.group) \
        .delete()
    return group_detail(request)


def start_group_map_print_job(request):
    # TODO: implement
    pass


def give_user_mapping_priveleges(request, username):
    mapper_context = _grant_mapping_access(request.group, username,
                                           is_approved=True)
    mail_context = notify_group_mapping_approved(request, request.group,
                                                 username)
    return merge(mapper_context, mail_context)


def remove_user_mapping_priveleges(request, username):
    return _grant_mapping_access(request.group, username, is_approved=False)


def _grant_mapping_access(group, username, is_approved):
    mapper, created = TrustedMapper.objects.update_or_create(
        group=group,
        user__username=username,
        defaults={'is_approved': is_approved})
    return {
        'mapper': mapper
    }


def request_mapper_status(request):
    user, group = request.user, request.group
    if not user_is_eligible_to_become_trusted_mapper(user, group):
        return HttpResponseForbidden()
    mapper, created = TrustedMapper.objects.update_or_create(
        group=group, user=user)
    return {
        'success': True
    }


def group_unmapped_territory_geojson(request, group_id):
    # Get unmapped blockfaces
    blockfaces = Blockface.objects.filter(is_available=True)

    my_territory_q = Q(territory__group_id=group_id)

    if request.body:
        # Get potentially selectable blockfaces in polygon
        # (those in my territory or unclaimed)
        point_list = json.loads(request.body)
        point_list.append(point_list[0])  # Close the polygon
        polygon = Polygon((point_list))

        no_reservations_q = \
            Q(blockfacereservation__isnull=True) \
            | Q(blockfacereservation__canceled_at__isnull=False) \
            | Q(blockfacereservation__expires_at__lt=now())
        nobodys_territory_q = Q(territory__group_id=None)
        unclaimed_q = no_reservations_q & nobodys_territory_q

        blockfaces = blockfaces \
            .filter(geom__within=polygon) \
            .filter(my_territory_q | unclaimed_q) \
            .distinct()

        # Return just blockface data
        # (skipping expensive queries to make tiler URLs)
        return _make_blockface_data_result(blockfaces)

    else:
        # Get all blockfaces in group's territory
        blockfaces = blockfaces.filter(my_territory_q)
        return _make_blockface_and_tiler_urls_result(
            request, blockfaces, group_id)


def group_update_territory(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    _update_territory(group, request)

    # Recreate PDF maps to show updated group territory
    _update_event_maps(group)

    result_blockfaces = Blockface.objects.filter(territory__group=group)
    return _make_blockface_and_tiler_urls_result(
        request, result_blockfaces, group_id)


@transaction.atomic
def _update_territory(group, request):
    new_block_ids = set([int(id) for id in json.loads(request.body)])
    old_block_ids = set(Territory.objects
                        .filter(group=group)
                        .values_list('blockface_id', flat=True))
    ids_to_add = new_block_ids - old_block_ids
    ids_to_kill = old_block_ids - new_block_ids
    # Make sure no unavailable or already-assigned blocks slipped in
    filtered_ids_to_add = Blockface.objects \
        .filter(id__in=ids_to_add) \
        .filter(is_available=True) \
        .filter(territory=None) \
        .values_list('id', flat=True)
    new_territory = [Territory(group=group, blockface_id=id)
                     for id in filtered_ids_to_add]
    Territory.objects.bulk_create(new_territory)
    Territory.objects \
        .filter(blockface_id__in=ids_to_kill) \
        .delete()


def _update_event_maps(group):
    events = Event.objects \
        .filter(group_id=group.id, begins_at__gt=now()) \
        .select_related('group')
    for event in events:
        create_event_map_pdf(event)


def _make_blockface_and_tiler_urls_result(request, blockfaces, group_id):
    result = {
        'blockDataList': _make_blockface_data_result(blockfaces),
        'tilerUrls': get_context_for_territory_admin_layer(request, group_id)
    }
    return result


def _make_blockface_data_result(blockfaces):
    block_data_list = [{'id': bf.id, 'geojson': bf.geom.json}
                       for bf in blockfaces]
    return block_data_list
