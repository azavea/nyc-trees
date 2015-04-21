# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_auto_20150416_1136'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='training_finished_wrapping_up',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
