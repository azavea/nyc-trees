# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import operator
import smtplib

import time

from datetime import timedelta

from boto.ses.exceptions import SESError

from django.conf import settings
from django.core.management.base import BaseCommand

from django.db import transaction, connection

from django.utils.timezone import now

from apps.core.models import TaskRun
from apps.survey.models import BlockfaceReservation
from apps.mail.views import send_reservation_reminder

COMMAND_NAME = 'apps.survey.management.commands.send_reminder_emails'
_ALREADY_SENT_MESSAGE = ('WARNING: reservation emails sent already today. '
                         'Doing nothing!')

_RESERVATIONS = 'reservations'
_REMAINING_RETRIES = 'remaining_retries'
_RETRY_COUNT = 4

_DONE = -1


class Command(BaseCommand):

    def _log(self, msg):
        self.stdout.write("%s: %s" % (COMMAND_NAME, msg))

    def handle(self, *args, **options):
        right_now = now()
        today = right_now.date()
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute('LOCK TABLE %s IN EXCLUSIVE MODE'
                               % TaskRun._meta.db_table)

            _, unlocked = (TaskRun
                           .objects
                           .get_or_create(name=COMMAND_NAME,
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
        soon = right_now + timedelta(days=settings.RESERVATION_REMINDER_WINDOW)
        expiring_soon = (BlockfaceReservation
                         .objects
                         .filter(reminder_sent_at__isnull=True,
                                 canceled_at__isnull=True,
                                 expires_at__gte=right_now,
                                 expires_at__lte=soon))

        if not expiring_soon:
            self._log("no emails sent")
            return

        users = {}
        for reservation in expiring_soon:
            user_data = users.get(reservation.user_id, {})
            user_reservations = user_data.get(_RESERVATIONS, [])
            user_reservations.append(reservation)
            user_data[_RESERVATIONS] = user_reservations
            user_data[_REMAINING_RETRIES] = _RETRY_COUNT
            users[reservation.user_id] = user_data

        remaining_retries = True
        while remaining_retries:
            remaining_retries = False
            for user_id, user_data in users.items():
                user_remaining_retries = user_data[_REMAINING_RETRIES]

                if user_remaining_retries == 0:
                    self._log("reached maximum retries for: %s ... SKIPPING"
                              % user_id)
                    continue
                elif user_remaining_retries == _DONE:
                    continue

                # sleep to avoid hitting request-per-second limits in AWS
                # given that we have plenty of time for this tasks to run
                time.sleep(0.5)

                reservations = user_data[_RESERVATIONS]
                ids = map(operator.attrgetter('id'), reservations)

                try:
                    send_reservation_reminder(
                        user_id, reservations=reservations)
                except (smtplib.SMTPException, SESError):
                    user_remaining_retries -= 1
                    self._log("triggering a retry for: %s - %s remaining"
                              % (user_id, user_remaining_retries))
                    user_data[_REMAINING_RETRIES] = user_remaining_retries
                    if user_remaining_retries > 0:
                        remaining_retries = True
                    continue

                (BlockfaceReservation
                 .objects
                 .filter(id__in=ids)
                 .update(reminder_sent_at=right_now))
                self._log("email sent to user_id: '%s'" % user_id)

                user_remaining_retries = _DONE
                user_data[_REMAINING_RETRIES] = user_remaining_retries
