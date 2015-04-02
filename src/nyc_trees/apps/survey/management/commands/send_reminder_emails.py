# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import operator
import smtplib

from datetime import timedelta

from boto.ses.exceptions import SESError

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
    def _log(self, msg):
        self.stdout.write("%s: %s" % (_COMMAND_NAME, msg))

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
            self._log(_ALREADY_SENT_MESSAGE)
            return

        # the reservation reminder email runs at 1am EST and is scoped
        # for three days. That means that the email that goes out on
        # monday at 1am will notify for all reservations expiring
        # Monday after 1am, all of Tuesday, and all of Wednesday, and
        # thursday before 1am if they haven't been notified already.
        # If something was expiring wednesday at 11pm, it would get another
        # shot on tuesday at 1am, and another shot on wednesday at 1am.
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
            self._log("no emails sent")
            return

        for user_id, reservations in user_reservations.items():
            try:
                send_reservation_reminder(user_id, reservations=reservations)
            except (smtplib.SMTPException, SESError):
                continue
            self._log("Email sent to user_id: '%s'" % user_id)
            ids = map(operator.attrgetter('id'), reservations)
            (BlockfaceReservation
             .objects
             .filter(id__in=ids)
             .update(reminder_sent_at=now()))
