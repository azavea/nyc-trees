# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0007_auto_20141226_1722'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(srid=3857),
        ),
        migrations.RunSQL(
            sql="SELECT UpdateGeometrySRID('event_event', 'location', 4326)",
            reverse_sql="SELECT UpdateGeometrySRID('event_event', 'location', 3857)",
            state_operations=[migrations.AlterField(
                model_name='event',
                name='location',
                field=django.contrib.gis.db.models.fields.PointField(srid=4326),
            )]
        ),
    ]
