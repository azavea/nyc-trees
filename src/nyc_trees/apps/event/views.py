# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.gis.geos import Point
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.timezone import get_current_timezone

from apps.core.forms import EmailForm
from apps.core.models import Group

from apps.event.forms import EventForm
from apps.event.models import Event

from apps.event.event_list import (immediate_events, all_events)


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
    user = request.user
    group = get_object_or_404(Group, slug=group_slug)
    event = get_object_or_404(Event, group=group.pk, slug=event_slug)
    rsvp_count = event.eventregistration_set.count()
    return {
        'group': group,
        'event': event,
        'is_admin': user == group.admin,
        'can_rsvp': rsvp_count < event.max_attendees,
        'rsvp_count': rsvp_count,
        'group_detail_url': reverse('group_detail', kwargs={
            'group_slug': group.slug
        }),
        'group_events_url': reverse('events', kwargs={
            'group_slug': group.slug
        }),
        'event_edit_url': reverse('event_edit', kwargs={
            'group_slug': group.slug,
            'event_slug': event.slug
        }),
        'rsvp_url': '',
        'share_url': ''
    }


def event_email_page(request, group_slug, event_slug):
    event = get_object_or_404(Event, slug=event_slug, group__slug=group_slug)
    return {
        'event': event,
        'group': event.group,
        'rsvp_count': event.eventregistration_set.count(),
        'form': EmailForm(),
        'message_sent': False
    }


def event_email(request, group_slug, event_slug):
    event = get_object_or_404(Event, slug=event_slug, group__slug=group_slug)
    form = EmailForm(request.POST)
    rsvps = event.eventregistration_set.all()

    message_sent = False
    if form.is_valid():
        # We need to send emails one-by-one, or everyone will be in the same
        # "to" line in the email
        for rsvp in rsvps.select_related('user'):
            rsvp.user.email_user(form.cleaned_data['subject'],
                                 form.cleaned_data['body'],
                                 [event.contact_email])
        message_sent = True

    return {
        'event': event,
        'group': event.group,
        'rsvp_count': rsvps.count(),
        'form': form,
        'message_sent': message_sent
    }


def events_list_page(request):
    immediate_events_list = (immediate_events
                             .configure(chunk_size=3)
                             .as_context(request))
    all_events_list = (all_events
                       .configure(show_filters=True)
                       .as_context(request))

    return {'immediate_events': immediate_events_list,
            'all_events': all_events_list}


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
    # Django automatically converts datetime objects to the correct
    # timezone when rendering templates. However, model forms do *not*
    # handle this for us when rendering date or time form fields,
    # only datetime form fields.
    tz = get_current_timezone()
    group = get_object_or_404(Group, slug=group_slug)
    event = get_object_or_404(Event, group=group.pk, slug=event_slug)
    form_context = {
        # TODO: Remove initial location after adding client-side geocoding
        'location': Point(0, 0),
        'date': event.begins_at.astimezone(tz),
        'begins_at_time': event.begins_at.astimezone(tz),
        'ends_at_time': event.ends_at.astimezone(tz)
    }
    form = EventForm(instance=event, initial=form_context)
    return {
        'form': form,
        'group': group,
        'event': event
    }


def edit_event(request, group_slug, event_slug):
    group = get_object_or_404(Group, slug=group_slug)
    event = get_object_or_404(Event, group=group.pk, slug=event_slug)
    form = EventForm(request.POST.copy(), instance=event)
    form.data['group'] = group.pk

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(
            reverse('event_detail', kwargs={
                'group_slug': group.slug,
                'event_slug': event_slug
            }))
    return {
        'form': form,
        'group': group,
        'event': event
    }


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
