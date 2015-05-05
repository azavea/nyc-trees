# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.utils.timezone import now

from apps.census_admin.tasks import write_data_dictionary
from apps.core.management.commands.dump_db import MODELS


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        today = now().date()
        dump_id = today.isoformat()
        result = write_data_dictionary(MODELS, dump_id)
        url = default_storage.url(result[0])
        print('Data dictionary written. View at URL %s' % url)
