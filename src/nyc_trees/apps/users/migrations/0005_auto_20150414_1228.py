# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_trustedmapper_is_approved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='achievement',
            name='achievement_id',
            field=models.IntegerField(choices=[(1, 'In Pursuit of Mappiness'), (0, 'Ready, Set, Roll'), (2, 'Certified Mapper'), (3, 'Free Mapper'), (4, 'Map 50 Block Edges'), (5, 'Map 100 Block Edges'), (6, 'Map 200 Block Edges'), (7, 'Map 400 Block Edges'), (8, 'Map 1000 Block Edges'), (9, 'Map the Most Block Edges in NYC')]),
            preserve_default=True,
        ),
    ]
