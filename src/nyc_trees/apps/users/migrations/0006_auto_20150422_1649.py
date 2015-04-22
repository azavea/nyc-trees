# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20150414_1228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='achievement',
            name='achievement_id',
            field=models.IntegerField(choices=[(1, 'In Pursuit of Mappiness'), (0, 'Ready, Set, Roll'), (2, 'Treerifically Trained'), (3, 'Counter Cultured'), (4, 'Rolling Revolutionary'), (5, 'Mapping Machine'), (6, 'Sprout Mapper'), (7, 'Seedling Mapper'), (8, 'Sapling Mapper'), (9, 'Mayoral Mapper')]),
            preserve_default=True,
        ),
    ]
