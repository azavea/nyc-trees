# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0008_auto_20150106_1825'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='map_pdf_filename',
            field=models.CharField(default='', max_length=255, blank=True),
            preserve_default=True,
        ),
    ]
