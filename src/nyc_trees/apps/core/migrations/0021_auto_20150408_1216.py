# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20150323_1457'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='progress_page_help_shown',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='reservations_page_help_shown',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
