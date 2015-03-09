# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0012_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tree',
            name='curb_location',
            field=models.CharField(max_length=25, choices=[('OnCurb', 'Along the curb'), ('OffsetFromCurb', 'Offset from the curb')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='guards',
            field=models.CharField(blank=True, max_length=15, choices=[('None', 'Not installed'), ('Helpful', 'Helpful'), ('Harmful', 'Harmful'), ('Unsure', 'Unsure')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='sidewalk_damage',
            field=models.CharField(blank=True, max_length=15, choices=[('NoDamage', 'No damage'), ('Damage', 'Cracks or raised')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='status',
            field=models.CharField(max_length=15, choices=[('Alive', 'Tree is alive'), ('Dead', 'Tree is dead'), ('Stump', 'Stump < 24"')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='stewardship',
            field=models.CharField(blank=True, max_length=15, choices=[('None', 'Zero'), ('1or2', '1-2'), ('3or4', '3-4'), ('4orMore', '4+')]),
            preserve_default=True,
        ),
    ]
