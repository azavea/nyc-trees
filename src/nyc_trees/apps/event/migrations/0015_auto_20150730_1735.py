# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def clear_event_pdfs(apps, schema_editor):
    Event = apps.get_model("event", "Event")
    for event in Event.objects.all():
        event.map_pdf_filename = ''
        event.save()

def no_op(*args, **kwargs):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0014_auto_20150506_1634'),
    ]

    operations = [
        migrations.RunPython(clear_event_pdfs, reverse_code=no_op),
    ]
