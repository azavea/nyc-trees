# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0009_blockface_expert_required'),
    ]

    operations = [
        migrations.AddField(
            model_name='tree',
            name='stump_diameter',
            field=models.PositiveIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='circumference',
            field=models.PositiveIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='distance_to_end',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='distance_to_tree',
            field=models.FloatField(),
            preserve_default=True,
        ),
    ]
