# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import shortuuid
import subprocess

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse

from celery import task


def create_event_map_pdf(request, event):
    filename = "event_map/%s_%s.pdf" % (event.slug, shortuuid.uuid())
    event.map_pdf_filename = filename
    event.clean_and_save()

    url = reverse('printable_event_map', kwargs={
        'group_slug': event.group.slug,
        'event_slug': event.slug,
        })

    create_pdf(request, url, filename)


def create_reservations_map_pdf(request, reservation_ids):
    user = request.user
    user.reservation_ids_in_map_pdf = reservation_ids

    if reservation_ids == '':
        # User has no reservations. Clear filename to indicate no map.
        user.reservations_map_pdf_filename = ''
        user.clean_and_save()

    else:
        filename = "reservations_map/%s_%s.pdf" % (
            user.username, shortuuid.uuid())
        user.reservations_map_pdf_filename = filename
        user.clean_and_save()

        url = reverse('printable_reservations_map')

        create_pdf(request, url, filename)


def create_pdf(request, url, filename):
    host = request.get_host()
    if hasattr(request, 'session'):  # prevent test failure
        session_id = request.session.session_key
        create_and_save_pdf.delay(session_id, host, url, filename)


@task(bind=True, max_retries=4, default_retry_delay=0)
def create_and_save_pdf(self, session_id, host, url, filename):
    try:
        if host.endswith(':8000'):
            protocol = 'http'  # development
            host = 'localhost'
        else:
            protocol = 'https'  # production

        pdf_bytes = subprocess.check_output(
            ['phantomjs', '--ssl-protocol=tlsv1', 'js/backend/url2pdf.js',
             session_id, protocol, host, url, '1.0'])

        content = ContentFile(pdf_bytes)
        default_storage.save(filename, content)

        return filename

    except subprocess.CalledProcessError as e:
        if self.request.retries < self.max_retries:
            self.retry(exc=e)
        else:
            return None


def url_if_cooked(filename):
    if filename and default_storage.exists(filename):
        return default_storage.url(filename)
    else:
        return None
