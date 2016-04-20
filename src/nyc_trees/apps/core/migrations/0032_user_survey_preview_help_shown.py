# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_auto_20150513_1536'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='survey_preview_help_shown',
            field=models.BooleanField(default=False, help_text='Seen preview button help text on Survey page?'),
            preserve_default=True,
        ),
    ]
