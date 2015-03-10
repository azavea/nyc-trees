# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_remove_user_is_census_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='affiliation',
            field=models.CharField(default='', max_length=255, blank=True),
            preserve_default=True,
        ),
    ]
