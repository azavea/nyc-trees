# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_user_training_finished_intro_quiz'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='field_training_complete',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
