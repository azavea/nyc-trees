# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20150203_1604'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='individual_mapper',
            field=models.NullBooleanField(),
            preserve_default=True,
        ),
    ]
