# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from celery import task
from apps.core.models import User
from apps.mail import MessageType
from apps.mail.libs import send_to, storage_pdf_to_attachment
from apps.survey.models import Blockface
from apps.event.models import Event


@task
def notify_reservation_confirmed(pdf_filename, user_id, blockface_ids):
    user = User.objects.get(id=user_id)
    blockfaces = Blockface.objects.filter(id__in=blockface_ids)
    if pdf_filename:
        attachments = [storage_pdf_to_attachment(pdf_filename)]
    else:
        attachments = None

    return send_to(user,
                   MessageType.NEW_RESERVATIONS_CONFIRMED,
                   blockfaces=blockfaces,
                   attachments=attachments)


@task
def notify_rsvp(pdf_filename, absolute_event_url, user_id, event_id):
    user = User.objects.get(pk=user_id)
    event = Event.objects.get(pk=event_id)
    if pdf_filename:
        attachments = [storage_pdf_to_attachment(pdf_filename)]
    else:
        attachments = None

    return send_to(user,
                   MessageType.RSVP,
                   event=event,
                   event_url=absolute_event_url,
                   attachments=attachments)
