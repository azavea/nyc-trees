# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_group_allows_individual_mappers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='contact_info',
            field=models.CharField(default='', max_length=255, blank=True),
        ),
    ]
