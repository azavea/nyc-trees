# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import os

from urlparse import urljoin

from django.core.urlresolvers import reverse
from django.core.files.storage import default_storage
from django.contrib.sites.models import Site
from django.conf import settings

from celery import task

from apps.core.models import User
from apps.mail import MessageType
from apps.mail.libs import send_to, pdf_to_attachment
from apps.survey.models import Blockface, BlockfaceReservation
from apps.event.models import Event


@task
def notify_reservation_confirmed(pdf_filename, user_id, reservation_ids):
    if not reservation_ids:
        # Return some meaningful log output for this celery task.
        return {
            'user_id': user_id,
            'success': False,
            'message': 'No new reservations to confirm'
        }

    user = User.objects.get(id=user_id)
    reservations = BlockfaceReservation.objects.filter(id__in=reservation_ids)
    blockface_ids = reservations.values_list('blockface_id', flat=True)
    blockfaces = Blockface.objects.filter(id__in=blockface_ids)
    expiration_date = reservations[0].expires_at
    attachments = []
    is_mapping_with_paper = False

    if pdf_filename:
        attachment = pdf_to_attachment(default_storage.open, pdf_filename)
        attachments.append(attachment)
    if reservations.filter(is_mapping_with_paper=True).exists():
        path = os.path.join(settings.STATIC_ROOT,
                            'TreesCount2015_worksheet.pdf')
        attachments.append(pdf_to_attachment(open, path))
        is_mapping_with_paper = True

    root_url = 'http://%s' % Site.objects.get_current().domain
    reservations_url = urljoin(root_url, reverse('reservations'))

    return send_to(user,
                   MessageType.NEW_RESERVATIONS_CONFIRMED,
                   blockfaces=blockfaces,
                   is_mapping_with_paper=is_mapping_with_paper,
                   reservations_url=reservations_url,
                   expiration_date=expiration_date,
                   attachments=attachments)


@task
def notify_rsvp(pdf_filename, absolute_event_url, user_id, event_id):
    user = User.objects.get(pk=user_id)
    event = Event.objects.get(pk=event_id)
    if pdf_filename:
        attachments = [pdf_to_attachment(default_storage.open, pdf_filename)]
    else:
        attachments = None

    return send_to(user,
                   MessageType.RSVP,
                   event=event,
                   event_url=absolute_event_url,
                   attachments=attachments)


@task
def notify_after_event_checkin(user_id):
    return send_to(User.objects.get(pk=user_id),
                   MessageType.AFTER_EVENT_CHECKIN)
