# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.gis.geos import Point
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import (HttpResponseRedirect, HttpResponseForbidden,
                         HttpResponseNotAllowed)
from django.shortcuts import get_object_or_404
from django.utils.timezone import get_current_timezone

from apps.core.forms import EmailForm

from apps.event.forms import EventForm
from apps.event.models import Event, EventRegistration

from apps.event.event_list import (EventList, immediate_events, all_events)

from apps.event.helpers import user_is_rsvped_for_event


def event_dashboard(request):
    # TODO: implement
    pass


def add_event(request):
    form = EventForm(request.POST.copy())
    form.data['group'] = request.group.pk

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(
            reverse('group_edit', kwargs={'group_slug': request.group.slug}))
    return {
        'form': form,
        'group': request.group
    }


def add_event_page(request):
    # TODO: Remove initial location after adding client-side geocoding
    form = EventForm(initial={'location': Point(0, 0)})
    return {
        'form': form,
        'group': request.group
    }


def event_detail(request, event_slug):
    user = request.user
    event = get_object_or_404(Event, group=request.group, slug=event_slug)
    rsvp_count = event.eventregistration_set.count()
    return {
        'group': request.group,
        'event': event,
        'is_admin': user == request.group.admin,
        'can_rsvp': rsvp_count < event.max_attendees,
        'is_rsvped': user_is_rsvped_for_event(user, event),
        'rsvp_count': rsvp_count,
        'group_events_url': reverse('events', kwargs={
            'group_slug': request.group.slug
        }),
        'event_edit_url': reverse('event_edit', kwargs={
            'group_slug': request.group.slug,
            'event_slug': event.slug
        }),
        'rsvp_url': reverse('event_registration', kwargs={
            'group_slug': request.group.slug,
            'event_slug': event.slug
        }),
        'share_url': ''
    }


def event_email_page(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug,
                              group=request.group)
    return {
        'event': event,
        'group': event.group,
        'rsvp_count': event.eventregistration_set.count(),
        'form': EmailForm(),
        'message_sent': False
    }


def event_email(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug, group=request.group)
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
                       .configure(filterset_name=EventList.trainingFilters,
                                  active_filter=EventList.Filters.ALL)
                       .as_context(request))

    return {'immediate_events': immediate_events_list,
            'all_events': all_events_list}


def events_list_page_partial(request):
    # TODO: implement
    pass


def events_list_feed(request):
    # TODO: implement
    pass


def delete_event(request, event_slug):
    # TODO: implement
    pass


def edit_event_page(request, event_slug):
    # Django automatically converts datetime objects to the correct
    # timezone when rendering templates. However, model forms do *not*
    # handle this for us when rendering date or time form fields,
    # only datetime form fields.
    tz = get_current_timezone()
    event = get_object_or_404(Event, group=request.group, slug=event_slug)
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
        'group': request.group,
        'event': event
    }


def edit_event(request, event_slug):
    event = get_object_or_404(Event, group=request.group, slug=event_slug)
    form = EventForm(request.POST.copy(), instance=event)
    form.data['group'] = request.group.pk

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(
            reverse('event_detail', kwargs={
                'group_slug': request.group.slug,
                'event_slug': event_slug
            }))
    return {
        'form': form,
        'group': request.group,
        'event': event
    }


def event_popup_partial(request, event_slug):
    # TODO: implement
    pass


@transaction.atomic
def register_for_event(request, event_slug):
    event = get_object_or_404(Event, group=request.group, slug=event_slug)
    if event.has_space_available and not user_is_rsvped_for_event(request.user,
                                                                  event):
        EventRegistration.objects.create(user=request.user, event=event)
    return event_detail(request, event_slug)


@transaction.atomic
def cancel_event_registration(request, event_slug):
    event = get_object_or_404(Event, group=request.group, slug=event_slug)
    if user_is_rsvped_for_event(request.user, event):
        EventRegistration.objects\
                         .filter(user=request.user, event=event)\
                         .delete()
    return event_detail(request, event_slug)


def start_event_map_print_job(request, event_slug):
    # TODO: implement
    pass


def event_check_in_page(request, event_slug):
    event = get_object_or_404(Event, group=request.group, slug=event_slug)
    rsvps = EventRegistration.objects.filter(event=event)
    users = [(row.user, row.did_attend) for row in rsvps]
    return {
        'group': request.group,
        'event': event,
        'users': users
    }


@transaction.atomic
def check_in_user_to_event(request, event_slug, username):
    if request.method == 'POST':
        did_attend = True
    elif request.method == 'DELETE':
        did_attend = False
    else:
        return HttpResponseNotAllowed()

    event = get_object_or_404(Event, group=request.group, slug=event_slug)
    try:
        rsvp = EventRegistration.objects.get(event=event,
                                             user__username=username)
        rsvp.did_attend = did_attend
        rsvp.save()
    except EventRegistration.DoesNotExist:
        return HttpResponseForbidden()

    return {
        'group': request.group,
        'event': event,
        'user': rsvp.user,
        'did_attend': did_attend
    }


def email_event_registered_users(request, event_slug):
    # TODO: implement
    pass
