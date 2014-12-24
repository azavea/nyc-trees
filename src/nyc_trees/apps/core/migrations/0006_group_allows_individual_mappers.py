# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_remove_user_opt_in_events_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='allows_individual_mappers',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
