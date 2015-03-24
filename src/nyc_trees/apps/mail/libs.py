# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from email.mime.application import MIMEApplication

from django.core.files.storage import default_storage


def storage_pdf_to_attachment(path):
    with default_storage.open(path) as pdf:
        return MIMEApplication(pdf.read(), 'pdf')
