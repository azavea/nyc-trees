# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_group_border'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE core_group ALTER COLUMN border TYPE geometry(MultiPolygon, 4326) USING ST_Multi(border)",
            state_operations=[migrations.AlterField(
                model_name='group',
                name='border',
                field=django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326, null=True, blank=True),
                preserve_default=True,
            )]
        ),
    ]
