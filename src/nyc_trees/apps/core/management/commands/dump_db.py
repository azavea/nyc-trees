# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from celery import chord

from django.core.management.base import BaseCommand
from django.db import transaction, connection
from django.utils.timezone import now

from apps.core.models import TaskRun, User, Group
from apps.census_admin.tasks import (dump_model, dump_trees_to_shapefile,
                                     dump_blockface_to_shapefile, zip_dumps,
                                     dump_events_to_shapefile,
                                     write_data_dictionary)


def _except(Model, *omitted_fields):
    return [f.name for f in Model._meta.local_fields
            if f.name not in omitted_fields]


TASK_NAME = 'dump_db'

CUSTOM_CSV_MODELS = [
    ('apps.core.models.User', _except(User, 'password')),
    ('apps.core.models.Group', _except(Group, 'border')),
]

CSV_MODELS = [
    'apps.event.models.EventRegistration',
    'apps.survey.models.BlockfaceReservation',
    'apps.survey.models.Species',
    'apps.survey.models.Survey',
    'apps.survey.models.Territory',
    'apps.users.models.Achievement',
    'apps.users.models.Follow',
    'apps.users.models.TrainingResult',
    'apps.users.models.TrustedMapper'
]

GEO_MODELS = [
    'apps.event.models.Event',
    'apps.survey.models.Blockface',
    'apps.survey.models.Tree',
]

ALL_CSV_MODELS = [name for name, _ in CUSTOM_CSV_MODELS] + CSV_MODELS

MODELS = ALL_CSV_MODELS + GEO_MODELS


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

        dump_model_tasks = [dump_model.s(fqn, None, dump_id)
                            for fqn in CSV_MODELS]
        dump_model_tasks += [dump_model.s(fqn, fields, dump_id)
                             for fqn, fields in CUSTOM_CSV_MODELS]
        dump_model_tasks += [dump_trees_to_shapefile.s(dump_id),
                             dump_blockface_to_shapefile.s(dump_id),
                             dump_events_to_shapefile.s(dump_id),
                             write_data_dictionary.s(MODELS, dump_id),
                             ]

        dump_tasks = chord(dump_model_tasks, zip_dumps.s(dump_id))
        dump_tasks.apply_async()

        TaskRun.objects.create(name=TASK_NAME,
                               date_started=today,
                               task_result_id=dump_tasks.id)
