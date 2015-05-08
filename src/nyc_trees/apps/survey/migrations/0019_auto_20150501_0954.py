# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0018_auto_20150422_1214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tree',
            name='status',
            field=models.CharField(max_length=15, choices=[('Alive', 'Tree is alive'), ('Dead', 'Tree is dead'), ('Stump', 'Stump (<24" tall)')]),
            preserve_default=True,
        ),
    ]
