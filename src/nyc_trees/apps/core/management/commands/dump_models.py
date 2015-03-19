# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.core.management.base import BaseCommand

from apps.core.tasks import dump_models


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if len(args) > 0:
            dump_id = args[0]
        else:
            dump_id = None
        file_paths = dump_models(dump_id=dump_id)
        for path in file_paths:
            print(path)
