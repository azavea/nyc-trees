# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import apps.users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20150505_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='achievement',
            name='achievement_id',
            field=models.IntegerField(help_text=apps.users.models.achievement_help_text, choices=[(1, 'In Pursuit of Mappiness'), (0, 'Ready, Set, Roll'), (2, 'Treerifically Trained'), (3, 'Counter Cultured'), (4, 'Rolling Revolutionary'), (5, 'Mapping Machine'), (6, 'Sprout Mapper'), (7, 'Seedling Mapper'), (8, 'Sapling Mapper'), (9, 'Mayoral Mapper'), (10, 'Lavender Linden'), (11, 'Magenta Maple'), (12, 'Silver Sophora'), (13, 'Gold Gingko'), (14, 'Platinum Planetree'), (15, 'Four Season Mapper')]),
            preserve_default=True,
        ),
    ]
