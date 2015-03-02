# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0008_auto_20150225_0959'),
    ]

    operations = [
        migrations.AddField(
            model_name='blockface',
            name='expert_required',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
