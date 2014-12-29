# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from apps.core.helpers import user_is_group_admin
from apps.core.models import Group
from apps.users.models import Follow

from apps.users.forms import GroupSettingsForm
from apps.event.models import Event
from apps.event.event_list import EventList


def group_list_page(request):
    # TODO: pagination
    groups = Group.objects.all()
    group_ids = Follow.objects.filter(user_id=request.user.id) \
        .values_list('group_id', flat=True)
    user_is_following = [group.id in group_ids for group in groups]

    return {
        'groups': zip(groups, user_is_following)
    }


def _group_events(request, group_slug):
    return Event.objects.filter(group__slug=group_slug, is_private=False)

group_events = EventList(_group_events, 'groups/partials/event_list.html')


def group_detail(request):
    group = request.group
    events = (group_events
              .configure(chunk_size=2,
                         active_filter=EventList.Filters.CURRENT,
                         filterset_name=EventList.chronoFilters)
              .as_context(request, group_slug=group.slug))
    user_is_following = Follow.objects.filter(user_id=request.user.id,
                                              group=group).exists()
    show_mapper_request = group.allows_individual_mappers and \
        not user_is_group_admin(request.user, group)

    return {
        'group': group,
        'event_list': events,
        'user_can_edit_group': user_is_group_admin(request.user, group),
        'user_is_following': user_is_following,
        'edit_url': reverse('group_edit', kwargs={'group_slug': group.slug}),
        'show_mapper_request': show_mapper_request
    }


def redirect_to_group_detail(request):
    return HttpResponseRedirect(
        reverse('group_detail', kwargs={
            'group_slug': request.group.slug
        }))


def edit_group(request):
    form = GroupSettingsForm(instance=request.group, label_suffix='')
    context = {
        'group': request.group,
        'form': form,
        'group_slug': request.group.slug,
    }
    return context


def update_group_settings(request):
    form = GroupSettingsForm(request.POST, instance=request.group)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(request.group.get_absolute_url())
    else:
        context = {
            'form': form,
            'group_slug': request.group.slug
        }
        return context


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
