# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.core.management.base import BaseCommand
from django.db import transaction, connection
from django.utils.timezone import now

from apps.core.models import TaskRun
from apps.core.tasks import dump_models

TASK_NAME = 'dump_models'


class Command(BaseCommand):

    @transaction.atomic
    def handle(self, *args, **kwargs):

        today = now().date()

        # Attempt to acquire a lock to the taskrun table, blocking if another
        # transaction already has a lock.
        # Since we create new rows to indicate when a task has been run, we
        # need to lock the entire taskrun table, not just a subset of rows.
        # This prevents us from using the builtin 'select_for_update'
        with connection.cursor() as cursor:
            cursor.execute('LOCK TABLE core_taskrun IN EXCLUSIVE MODE')

        if TaskRun.objects.filter(name=TASK_NAME, date_started=today).exists():
            self.stdout.write(
                'Task {} has already been started today, skipping'.format(
                    TASK_NAME))
            return

        if len(args) > 0:
            dump_id = args[0]
        else:
            dump_id = None
        file_paths = dump_models(dump_id=dump_id)
        for path in file_paths:
            print(path)

        # Using 0 as a task_result_id because this is currently not
        # a celery task
        TaskRun.objects.create(name=TASK_NAME,
                               date_started=today,
                               task_result_id=0)
