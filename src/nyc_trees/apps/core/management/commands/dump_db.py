# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from celery import chord

from django.core.management.base import BaseCommand
from django.db import transaction, connection
from django.utils.timezone import now

from apps.core.models import TaskRun
from apps.census_admin.tasks import (dump_model, dump_trees_to_shapefile,
                                     dump_blockface_to_shapefile, zip_dumps,
                                     dump_events_to_shapefile)

TASK_NAME = 'dump_db'

MODELS = ['apps.core.models.User',
          'apps.core.models.Group',
          'apps.event.models.EventRegistration',
          'apps.survey.models.BlockfaceReservation',
          'apps.survey.models.Species',
          'apps.survey.models.Survey',
          'apps.survey.models.Territory',
          'apps.users.models.Achievement',
          'apps.users.models.Follow',
          'apps.users.models.TrainingResult',
          'apps.users.models.TrustedMapper']


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

        dump_id = today.isoformat()

        dump_model_tasks = [dump_model.s(fqn, dump_id) for fqn in MODELS]
        dump_model_tasks += [dump_trees_to_shapefile.s(dump_id),
                             dump_blockface_to_shapefile.s(dump_id),
                             dump_events_to_shapefile.s(dump_id)]

        dump_tasks = chord(dump_model_tasks, zip_dumps.s(dump_id))
        dump_tasks.apply_async()

        TaskRun.objects.create(name=TASK_NAME,
                               date_started=today,
                               task_result_id=dump_tasks.id)
