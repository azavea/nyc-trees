# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from apps.core.models import Group
from apps.users.forms import GroupSettingsForm
from apps.event.models import Event
from apps.event.event_list import EventList


def group_list_page(request):
    return {
        'groups': Group.objects.all()
    }


def group_detail(request):
    events = Event.objects.filter(group_id=request.group.pk, is_private=False)

    return {
        'group': request.group,
        'event_list': EventList.simple_context(request, events),
        # TODO: check if user is group admin or census admin
        'user_can_edit_group': True,
        'edit_url': reverse('group_edit', kwargs={
            'group_slug': request.group.slug})
    }


def edit_group(request):
    form = GroupSettingsForm(instance=request.group, label_suffix='')
    context = {
        'form': form,
        'group_slug': request.group.slug
    }
    return context


def update_group_settings(request):
    form = GroupSettingsForm(request.POST, instance=request.group)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(
            reverse('group_detail', kwargs={'group_slug': request.group.slug}))
    else:
        context = {
            'form': form,
            'group_slug': request.group.slug
        }
        return context


def follow_group(request):
    # TODO: implement
    pass


def unfollow_group(request):
    # TODO: implement
    pass


def start_group_map_print_job(request):
    # TODO: implement
    pass


def give_user_mapping_priveleges(request, username):
    # TODO: implement
    pass


def remove_user_mapping_priveleges(request, username):
    # TODO: implement
    pass
