# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_remove_user_online_training_complete'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='training_finished_intro_quiz',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
