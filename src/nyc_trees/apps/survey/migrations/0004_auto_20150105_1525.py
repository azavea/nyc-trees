# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0003_auto_20141231_1235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blockface',
            name='geom',
            field=django.contrib.gis.db.models.fields.MultiLineStringField(srid=3857, db_column='the_geom_webmercator'),
        ),
    ]
