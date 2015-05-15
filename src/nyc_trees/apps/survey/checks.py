# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from datetime import timedelta

from django.utils.timezone import now

from apps.core.models import TaskRun
from apps.survey.management.commands.send_reminder_emails import COMMAND_NAME


def cron_jobs():
    return {
        'cron_jobs': [
            send_reminder_emails()
        ]
    }


def send_reminder_emails():
    task = TaskRun.objects.filter(name=COMMAND_NAME) \
                          .order_by('-date_started').first()

    if task:
        last_ran_at = task.date_started
        ok = now().date() - task.date_started <= timedelta(days=1)
    else:
        last_ran_at = 'never'
        ok = True

    return {
        'name': 'send_reminder_emails',
        'last_ran_at': last_ran_at,
        'ok': ok,
    }
