# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import operator
import smtplib

from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand

from django.db import transaction, connection

from django.utils.timezone import now

from apps.core.models import TaskRun
from apps.survey.models import BlockfaceReservation
from apps.mail.views import send_reservation_reminder

_COMMAND_NAME = 'apps.survey.management.commands.send_reminder_emails'
_ALREADY_SENT_MESSAGE = ('WARNING: Reservation emails sent already today. '
                         'Doing nothing!')


class Command(BaseCommand):
    def handle(self, *args, **options):
        today = now().date()
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute('LOCK TABLE %s IN EXCLUSIVE MODE'
                               % TaskRun._meta.db_table)

            _, unlocked = (TaskRun
                           .objects
                           .get_or_create(name=_COMMAND_NAME,
                                          date_started=today))

        if not unlocked:
            self.stdout.write(_ALREADY_SENT_MESSAGE)
            return

        soon = now() + timedelta(days=settings.RESERVATION_REMINDER_WINDOW)
        expiring_soon = (BlockfaceReservation
                         .objects
                         .filter(reminder_sent_at__isnull=True,
                                 canceled_at__isnull=True,
                                 expires_at__lte=soon))

        user_reservations = {}

        for reservation in expiring_soon:
            user_data = user_reservations.get(reservation.user_id, [])
            user_data.append(reservation)
            user_reservations[reservation.user_id] = user_data

        if not user_reservations:
            self.stdout.write("no emails sent")
            return

        for user_id, reservations in user_reservations.items():
            try:
                send_reservation_reminder(user_id, reservations=reservations)
            except smtplib.SMTPException:
                continue
            self.stdout.write("Email sent to user_id: '%s'" % user_id)
            ids = map(operator.attrgetter('id'), reservations)
            (BlockfaceReservation
             .objects
             .filter(id__in=ids)
             .update(reminder_sent_at=now()))
