# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0015_auto_20150414_1228'),
    ]

    operations = [
        migrations.AddField(
            model_name='blockface',
            name='source',
            field=models.CharField(default='unknown', max_length=255),
            preserve_default=True,
        ),
    ]
