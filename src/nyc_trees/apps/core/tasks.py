# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import os
import uuid
import importlib
import tempfile

from djqscsv import write_csv

from django.conf import settings
from django.core.files.storage import default_storage

from libs.custom_storages import PrivateS3BotoStorage

# Using strings so we can easily transition to async tasks, which need
# serializable arguments
MODELS = ['apps.core.models.User',
          'apps.core.models.Group',
          'apps.event.models.Event',
          'apps.event.models.EventRegistration',
          'apps.survey.models.BlockfaceReservation',
          'apps.survey.models.Species',
          'apps.survey.models.Survey',
          'apps.survey.models.Territory',
          'apps.users.models.Achievement',
          'apps.users.models.Follow',
          'apps.users.models.TrainingResult',
          'apps.users.models.TrustedMapper']


if getattr(settings, 'PRIVATE_AWS_STORAGE_BUCKET_NAME', None):
    _storage = PrivateS3BotoStorage()
else:
    _storage = default_storage


def dump_model(fq_name, dump_id):
    _, temp_file_path = tempfile.mkstemp()
    Model = _model_from_fq_name(fq_name)
    with open(temp_file_path, 'w') as f:
        write_csv(Model.objects.all(), f)

    model_name = Model.__name__.lower()
    file_name = os.path.join(dump_id, model_name + '.csv')

    with open(temp_file_path, 'r') as f:
        destination_path = _storage.save(file_name, f)
    os.remove(temp_file_path)

    return destination_path


def dump_models(dump_id=None):
    if not dump_id:
        dump_id = str(uuid.uuid4())
    return map(lambda fqn: dump_model(fqn, dump_id), MODELS)


def _class_for_name(module_name, class_name):
    m = importlib.import_module(module_name)
    return getattr(m, class_name)


def _model_from_fq_name(fq_name):
    module_name, class_name = fq_name.rsplit('.', 1)
    return _class_for_name(module_name, class_name)
