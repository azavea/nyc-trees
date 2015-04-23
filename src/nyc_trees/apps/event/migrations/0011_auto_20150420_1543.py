# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0010_auto_20150414_1228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='title',
            field=models.CharField(max_length=255, validators=[django.core.validators.RegexValidator('[\\w][\\w\\s]+')]),
            preserve_default=True,
        ),
    ]
