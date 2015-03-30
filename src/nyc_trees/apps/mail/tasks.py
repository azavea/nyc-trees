# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from celery import task
from apps.core.models import User
from apps.mail import MessageType
from apps.mail.libs import send_to, storage_pdf_to_attachment
from apps.survey.models import Blockface


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
