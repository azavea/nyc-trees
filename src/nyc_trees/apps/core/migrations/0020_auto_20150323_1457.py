# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20150319_1136'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='reservation_ids_in_map_pdf',
            field=models.TextField(default='', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='reservations_map_pdf_filename',
            field=models.CharField(default='', max_length=255, blank=True),
            preserve_default=True,
        ),
    ]
