# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0004_auto_20150105_1525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blockface',
            name='geom',
            field=django.contrib.gis.db.models.fields.MultiLineStringField(srid=3857),
        ),
        migrations.RunSQL(
            sql="SELECT UpdateGeometrySRID('survey_blockface', 'geom', 4326)",
            reverse_sql="SELECT UpdateGeometrySRID('survey_blockface', 'geom', 3857)",
            state_operations=[migrations.AlterField(
                model_name='blockface',
                name='geom',
                field=django.contrib.gis.db.models.fields.MultiLineStringField(srid=4326),
            )]
        ),
    ]
