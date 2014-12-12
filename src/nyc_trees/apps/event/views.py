# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from apps.users.models import Follow
from apps.event.models import Event, EventRegistration
from django.contrib.gis.geos import Point
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from apps.core.models import Group
from apps.event.forms import EventForm


def event_dashboard(request, group_slug):
    # TODO: implement
    pass


def add_event(request, group_slug):
    group = get_object_or_404(Group, slug=group_slug)
    form = EventForm(request.POST.copy())
    form.data['group'] = group.pk

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(
            reverse('group_edit', kwargs={'group_slug': group.slug}))
    return {
        'form': form,
        'group': group
    }


def add_event_page(request, group_slug):
    group = get_object_or_404(Group, slug=group_slug)
    # TODO: Remove initial location after adding client-side geocoding
    form = EventForm(initial={'location': Point(0, 0)})
    return {
        'form': form,
        'group': group
    }


def event_detail(request, group_slug, event_slug):
    # TODO: implement
    return {}


def events_list_page(request):
    user = request.user
    user_registered_event_ids = set(EventRegistration.objects
                                    .filter(user_id=user.pk)
                                    .values_list('event_id', flat=True))
    make_event_info = lambda event: {'event': event,
                                     'user_is_registered':
                                     event.pk in user_registered_event_ids}
    all_events = Event.objects.all()

    if user.is_authenticated():
        follows = Follow.objects.filter(user_id=user.id)
        groups = follows.values_list('group', flat=True)
        followed_events = all_events.filter(group_id__in=groups)
        non_followed_events = all_events.exclude(pk__in=followed_events)
    else:
        followed_events = Event.objects.none()
        non_followed_events = all_events

    return {'followed_events': map(make_event_info, followed_events),
            'non_followed_events': map(make_event_info, non_followed_events)}


def events_list_page_partial(request):
    # TODO: implement
    pass


def events_list_feed(request):
    # TODO: implement
    pass


def delete_event(request, group_slug, event_slug):
    # TODO: implement
    pass


def edit_event_page(request, group_slug, event_slug):
    # TODO: implement
    return {}


def edit_event(request, group_slug, event_slug):
    # TODO: implement
    pass


def event_popup_partial(request, group_slug, event_slug):
    # TODO: implement
    pass


def register_for_event(request, group_slug, event_slug):
    # TODO: implement
    pass


def cancel_event_registration(request, group_slug, event_slug):
    # TODO: implement
    pass


def start_event_map_print_job(request, group_slug, event_slug):
    # TODO: implement
    pass


def event_check_in_page(request, group_slug, event_slug):
    # TODO: implement
    return {}


def check_in_user_to_event(request, group_slug, event_slug, username):
    # TODO: implement
    pass


def un_check_in_user_to_event(request, group_slug, event_slug, username):
    # TODO: implement
    pass


def email_event_registered_users(request, group_slug, event_slug):
    # TODO: implement
    pass
