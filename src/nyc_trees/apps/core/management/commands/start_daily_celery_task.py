# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.db import transaction
from django.core.management.base import BaseCommand
from django.utils.timezone import now

from nyc_trees.celery import debug_task

from apps.core.models import TaskRun


tasks = {
    'debug_task': debug_task
}


class Command(BaseCommand):
    """
    Starts a daily celery task, using DB locks to ensure that the task is
    only queued once even if this management command is called multiple times.
    """

    option_list = BaseCommand.option_list

    @transaction.atomic
    def handle(self, *args, **options):
        if len(args) != 1 or args[0] not in tasks.keys():
            raise Exception(
                'Expected option to be one of the following: [{}]'.format(
                    tasks.keys()))

        task_name = args[0]
        today = now().date()

        # select_for_update will block if there are other transactions running
        # which have also selected this table for update.
        task_runs = TaskRun.objects.select_for_update().filter(name=task_name)

        import time; time.sleep(10)

        if task_runs.filter(date_started=today).exists():
            self.stdout.write(
                'Task {} has already been started today, skipping'.format(
                    task_name))
            return

        result = tasks[task_name].delay()

        TaskRun.objects.create(name=task_name, date_started=today,
                               task_result_id=result.id)

        self.stdout.write('Started task {}'.format(task_name))
