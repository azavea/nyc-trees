# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from urlparse import urljoin

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.contrib.sites.models import Site

from apps.core.models import User

from apps.mail.libs import send_to
from apps.mail import MessageType


def notify_group_mapping_approved(request, group, username):
    user = get_object_or_404(User, username=username)
    reservations_url = request.build_absolute_uri(reverse('reservations'))
    return send_to(user,
                   MessageType.GROUP_MAPPING_APPROVED,
                   group=group,
                   reservations_url=reservations_url)


def notify_rsvp(request, user, event):
    relative_event_url = reverse('event_detail', kwargs={
        'group_slug': event.group.slug,
        'event_slug': event.slug
    })
    event_url = request.build_absolute_uri(relative_event_url)
    return send_to(user,
                   MessageType.RSVP,
                   event=event,
                   event_url=event_url)


def send_reservation_reminder(user_id, **kwargs):
    user = get_object_or_404(User, id=user_id)
    reservations_url = urljoin(
        'http://%s' % Site.objects.get_current().domain,
        reverse('reservations'))
    return send_to(user, MessageType.RESERVATION_REMINDER,
                   reservations_url=reservations_url,
                   **kwargs)
