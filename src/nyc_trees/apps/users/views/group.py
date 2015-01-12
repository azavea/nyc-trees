# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.timezone import now

from libs.formatters import humanize_bytes
from libs.sql import get_group_tree_count

from apps.core.helpers import user_is_group_admin
from apps.core.decorators import group_request
from apps.core.models import Group

from apps.users.models import Follow
from apps.users.forms import GroupSettingsForm

from apps.survey.models import Territory, Survey

from apps.event.models import Event, EventRegistration
from apps.event.event_list import EventList


def group_list_page(request):
    # TODO: pagination
    groups = Group.objects.order_by('name')
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
    group = request.group
    event_list = (group_detail_events
                  .configure(chunk_size=2,
                             active_filter=EventList.Filters.CURRENT,
                             filterset_name=EventList.chronoFilters)
                  .as_context(request, group_slug=group.slug))
    user_is_following = Follow.objects.filter(user_id=request.user.id,
                                              group=group).exists()
    show_mapper_request = group.allows_individual_mappers and \
        not user_is_group_admin(request.user, group)

    tree_count = get_group_tree_count(group)

    group_blocks = Territory.objects.filter(group=group)
    group_blocks_count = group_blocks.count()

    if group_blocks_count > 0:
        completed_blocks = Survey.objects \
            .filter(blockface__in=group_blocks) \
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
        .distinct('user') \
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
            'attendees': num_event_attendees
        }
    }


def redirect_to_group_detail(request):
    return HttpResponseRedirect(
        reverse('group_detail', kwargs={
            'group_slug': request.group.slug
        }))


def edit_group(request, form=None):
    group = request.group
    if not form:
        form = GroupSettingsForm(instance=request.group, label_suffix='')
    event_list = (group_edit_events
                  .configure(chunk_size=2,
                             active_filter=EventList.Filters.CURRENT,
                             filterset_name=EventList.chronoFilters)
                  .as_context(request, group_slug=group.slug))
    return {
        'group': group,
        'event_list': event_list,
        'form': form,
        'group_slug': group.slug,
        'max_image_size': humanize_bytes(
            settings.MAX_GROUP_IMAGE_SIZE_IN_BYTES, 0)
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
    # TODO: implement
    pass


def remove_user_mapping_priveleges(request, username):
    # TODO: implement
    pass
