# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import shortuuid

from datetime import timedelta
from django.utils import timezone

from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django.utils.text import slugify

from apps.core.models import User, Group

from libs.mixins import NycModel


# Amount of time before an event starts to display
# the "Starting soon" notification message.
STARTING_SOON_WINDOW = timedelta(hours=1)


class Event(NycModel, models.Model):
    # Once a group has events, we can't just delete the group, because
    # people could have registered to attend the group's events.
    group = models.ForeignKey(Group, on_delete=models.PROTECT)

    title = models.CharField(max_length=255)
    # blank=True is valid for 'slug', because we'll automatically create slugs
    slug = models.SlugField(blank=True)

    description = models.TextField(default='', blank=True)
    location_description = models.TextField(default='', blank=True)

    contact_email = models.EmailField(null=True)
    contact_name = models.CharField(max_length=255, default='', blank=True)

    begins_at = models.DateTimeField()
    ends_at = models.DateTimeField()

    address = models.CharField(max_length=1000)
    location = models.PointField()

    max_attendees = models.IntegerField()

    includes_training = models.BooleanField(default=False)
    is_canceled = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s - group '%s'" % (self.title, self.group)

    def clean(self):
        if not self.slug and not self.is_private:
            self.slug = slugify(self.title)
        elif not self.slug:
            self.slug = shortuuid.uuid()

    def training_summary(self):
        return 'Training' if self.includes_training else 'Mapping'

    @property
    def has_space_available(self):
        return self.eventregistration_set.count() < self.max_attendees

    def starting_soon(self, target_dt=None):
        """
        Return True if `target_dt` is within the event starting period.
        Argument `target_dt` defaults to `timezone.now` if omitted.
        """
        target_dt = target_dt or timezone.now()
        return target_dt >= self.begins_at - STARTING_SOON_WINDOW \
            and target_dt < self.ends_at

    def get_admin_checkin_url(self):
        return reverse('event_admin_check_in_page',
                       kwargs={'group_slug': self.group.slug,
                               'event_slug': self.slug})

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'group_slug': self.group.slug,
                                               'event_slug': self.slug})

    class Meta:
        unique_together = (("group", "slug"), ("group", "title"))


class EventRegistration(NycModel, models.Model):
    user = models.ForeignKey(User)
    # If users have registered for an event, we do not want to allow
    # the event to be deleted. If we do, the registration will
    # disappear from the User's profile page and they may show up to
    # an event on the day, not knowing it was canceled
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    did_attend = models.BooleanField(default=False)
    opt_in_emails = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'event')

    def __unicode__(self):
        return "'%s' registration for '%s'" % (self.user.username,
                                               self.event.title)
