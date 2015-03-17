# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import shortuuid
import subprocess

from django.core.files.base import ContentFile
from django.core.files.storage import DefaultStorage
from django.core.urlresolvers import reverse

from celery import task


def create_event_map_pdf(event):
    filename = "event_map/%s_%s.pdf" % (event.slug, shortuuid.uuid())
    event.map_pdf_filename = filename
    event.clean_and_save()

    url = reverse('printable_event_map', kwargs={
        'group_slug': event.group.slug,
        'event_slug': event.slug,
        })
    url = 'http://localhost' + url

    create_and_save_pdf.delay(url, event.map_pdf_filename)


@task()
def create_and_save_pdf(url, filename):
    pdf_bytes = url_to_pdf(url)
    content = ContentFile(pdf_bytes)
    DefaultStorage().save(filename, content)


def url_to_pdf(url, zoom_factor=1.0):
    pdf_bytes = subprocess.check_output(
        ['phantomjs', 'js/backend/url2pdf.js', url, str(zoom_factor)])
    return pdf_bytes
