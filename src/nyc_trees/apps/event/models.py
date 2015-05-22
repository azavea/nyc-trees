# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import shortuuid
from pytz import timezone, utc

from datetime import timedelta
from django.utils.timezone import now

from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db.models import Q
from django.utils.text import slugify

from apps.core.models import User, Group

from libs.mixins import NycModel
from libs.pdf_maps import url_if_cooked


# Amount of time before an event starts to display
# the "Starting soon" notification message.
STARTING_SOON_WINDOW = timedelta(hours=1)
# Amount of time after the event ends when emailing attendees is allowed
EMAIL_WINDOW = timedelta(days=7)


class Event(NycModel, models.Model):
    # Once a group has events, we can't just delete the group, because
    # people could have registered to attend the group's events.
    group = models.ForeignKey(
        Group, on_delete=models.PROTECT,
        help_text='Group sponsoring the event')

    title = models.CharField(
        max_length=255, validators=[RegexValidator(r'[\w][\w\s]+')],
        help_text='Name of event, for display')

    # blank=True is valid for 'slug', because we'll automatically create slugs
    slug = models.SlugField(
        blank=True, max_length=255,
        help_text='Short name used in URLs')

    description = models.TextField(
        default='', blank=True,
        help_text='Description of event, for display')
    location_description = models.TextField(
        default='', blank=True,
        help_text='How to find the event meeting location')

    contact_email = models.EmailField(
        null=True,
        help_text='Email address of contact person')
    contact_name = models.CharField(
        max_length=255, default='', blank=True,
        help_text='Name of contact person')

    begins_at = models.DateTimeField(help_text='When the event starts')
    ends_at = models.DateTimeField(help_text='When the event ends')

    address = models.CharField(
        max_length=1000,
        help_text='Approximate address of meeting location')
    location = models.PointField(help_text='Location displayed on event maps')

    max_attendees = models.IntegerField(
        help_text='Maximum number of people allowed to RSVP')

    includes_training = models.BooleanField(
        default=False,
        help_text='Is this a training event?')
    is_canceled = models.BooleanField(
        default=False,
        help_text='Has this event been canceled?')
    is_private = models.BooleanField(
        default=False,
        help_text='Is this a private event?')

    map_pdf_filename = models.CharField(
        max_length=255, default='', blank=True,
        help_text='S3 file path of event map PDF')

    objects = models.GeoManager()

    @staticmethod
    def raise_invalid_bounds(field_name):
        raise ValidationError({field_name: ["Must occur before end time"]})

    def __unicode__(self):
        return "%s - group '%s'" % (self.title, self.group)

    def clean(self):
        if self.begins_at > self.ends_at:
            self.raise_invalid_bounds('begins_at')

        if not self.slug and not self.is_private:
            self.slug = slugify(self.title)
        elif not self.slug:
            self.slug = shortuuid.uuid()

        xmin, ymin, xmax, ymax = settings.NYC_BOUNDS
        p = self.location
        if not p:
            raise ValidationError({'location': [
                "Location is required"
            ]})
        elif p.x < xmin or p.x > xmax or p.y < ymin or p.y > ymax:
            raise ValidationError({'location': [
                "Please choose a location in New York City"
            ]})

        rsvp_count = self.eventregistration_set.count()
        if self.max_attendees < rsvp_count:
            raise ValidationError({'max_attendees': [
                "Max attendees cannot be set to a value less than the number "
                "of people currently registered (%d)" % rsvp_count]})

    def training_summary(self):
        return 'Training' if self.includes_training else 'Mapping'

    @property
    def has_space_available(self):
        return self.eventregistration_set.count() < self.max_attendees

    def starting_soon(self, target_dt=None):
        """
        Return True if `target_dt` is within the event starting period.
        Argument `target_dt` defaults to `now` if omitted.
        """
        target_dt = target_dt or now()
        return target_dt >= self.begins_at - STARTING_SOON_WINDOW \
            and target_dt < self.ends_at

    def in_progress(self, target_dt=None):
        """
        Return True if event is in-progress in the context of `target_dt`.
        """
        target_dt = target_dt or now()
        return target_dt >= self.begins_at and target_dt < self.ends_at

    def is_mapping_allowed(self):
        now_utc = now()
        end_of_event_day = end_of_day_in_utc(self.ends_at)

        return self.begins_at <= now_utc <= end_of_event_day

    @property
    def has_started(self):
        return self.begins_at <= now()

    def get_admin_checkin_url(self):
        return reverse('event_admin_check_in_page',
                       kwargs={'group_slug': self.group.slug,
                               'event_slug': self.slug})

    def get_user_checkin_url(self):
        return reverse('event_user_check_in_page',
                       kwargs={'group_slug': self.group.slug,
                               'event_slug': self.slug})

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'group_slug': self.group.slug,
                                               'event_slug': self.slug})

    def get_shareable_url(self, request):
        return request.build_absolute_uri(self.get_absolute_url())

    @property
    def map_pdf_url(self):
        return url_if_cooked(self.map_pdf_filename)

    def is_past(self):
        return self.ends_at < now()

    @property
    def can_send_email(self):
        return (self.ends_at + EMAIL_WINDOW) >= now()

    class Meta:
        unique_together = (("group", "slug"), ("group", "title"))
        ordering = ['-begins_at']


class EventRegistration(NycModel, models.Model):
    user = models.ForeignKey(
        User,
        help_text='ID of user registering for event')
    # If users have registered for an event, we do not want to allow
    # the event to be deleted. If we do, the registration will
    # disappear from the User's profile page and they may show up to
    # an event on the day, not knowing it was canceled
    event = models.ForeignKey(
        Event, on_delete=models.PROTECT,
        help_text='ID of event registered for')
    did_attend = models.BooleanField(
        default=False,
        help_text='Was user  checked in to event?')
    opt_in_emails = models.BooleanField(
        default=True,
        help_text='Should user receive emails for this event?')

    class Meta:
        unique_together = ('user', 'event')

    @classmethod
    def my_events_now(cls, user):
        """
        Return a tuple of (attended events, non-attended events) for upcoming
        and in-progress events for which the user has RSVPd.
        """
        now_utc = now()

        end_of_day_utc = end_of_day_in_utc(now_utc)
        beginning_of_day_utc = start_of_day_in_utc(now_utc)

        # First filter to the events starting today
        # Then get those events which are starting soon or have yet to end, or
        # any attended events from today, which can be mapped until midnight
        registrations = EventRegistration.objects \
            .filter(user=user) \
            .filter(event__begins_at__gte=beginning_of_day_utc) \
            .filter(Q(did_attend=True, event__ends_at__lte=end_of_day_utc) |
                    Q(event__begins_at__lte=now_utc + STARTING_SOON_WINDOW,
                      event__ends_at__gt=now_utc)) \
            .prefetch_related('event')

        attended = [r.event for r in registrations if r.did_attend]
        non_attended = [r.event for r in registrations if not r.did_attend]

        # Group admins don't need to RSVP to be able to survey events.
        # These filters are derived from the query directly above.
        # The reason for copying this code rather than using queryset
        # composition is that the filters are different enough
        # (did_attend=True is irrelevant here) and the value of making this
        # DRY does not seem worth the effort at this point.
        admin_events = Event.objects \
            .filter(group__admin=user) \
            .filter(begins_at__gte=beginning_of_day_utc) \
            .filter(Q(ends_at__lte=end_of_day_utc) |
                    Q(begins_at__lte=now_utc + STARTING_SOON_WINDOW,
                      ends_at__gt=now_utc))
        non_attended = non_attended + list(admin_events)

        # Filter non-attended events from attended events.
        # The purpose of this is to fix an edge case where a group admin
        # has both RSVPd and checked-into their own event. Without this,
        # clicking the Treecorder link in the nav would display 2 links
        # (the checkin page and the survey page). Since we filter out
        # non-attended events, only the check-in page should appear for
        # group admins.
        attended = list(set(attended) - set(non_attended))

        return attended, non_attended

    @classmethod
    def next_event_starting_soon(cls, user):
        """
        Return the EventRegistration for the next event starting soon, or None
        """
        now_utc = now()
        events_now = Event.objects \
            .filter(begins_at__lte=now_utc + STARTING_SOON_WINDOW,
                    ends_at__gt=now_utc) \
            .order_by('begins_at')

        registrations = EventRegistration.objects \
            .filter(user=user) \
            .filter(event_id__in=events_now.values_list('id', flat=True)) \
            .order_by('event__begins_at') \
            .prefetch_related('event')

        # Since this method returns EventRegistrations instead of Events,
        # we have to union the above result with a list of artificial
        # EventRegistration objects.
        admin_events = events_now.filter(group__admin=user)
        admin_rsvps = [EventRegistration(user=user,
                                         event=event,
                                         did_attend=True)
                       for event in admin_events]
        registrations = admin_rsvps + list(registrations)

        return registrations[0] if registrations else None

    def __unicode__(self):
        return "'%s' registration for '%s'" % (self.user.username,
                                               self.event.title)


def end_of_day_in_utc(dt_utc):
    est_tz = timezone('US/Eastern')
    now_est = dt_utc.astimezone(est_tz)

    end_of_day_est = now_est.replace(hour=23, minute=59, second=59)

    return end_of_day_est.astimezone(utc)


def start_of_day_in_utc(dt_utc):
    est_tz = timezone('US/Eastern')
    now_est = dt_utc.astimezone(est_tz)

    start_of_day_est = now_est.replace(hour=0, minute=0, second=0)

    return start_of_day_est.astimezone(utc)
