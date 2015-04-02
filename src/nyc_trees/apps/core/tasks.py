# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from celery import task

from django.core.files.storage import default_storage


@task(bind=True, max_retries=15, default_retry_delay=2)
def wait_for_default_storage_file(self, filename):
    if default_storage.exists(filename):
        return filename
    else:
        self.retry()
