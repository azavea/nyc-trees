# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_auto_20150428_1529'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='survey_geolocate_help_shown',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
