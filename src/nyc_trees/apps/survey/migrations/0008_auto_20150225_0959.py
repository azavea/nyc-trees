# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0007_auto_20150202_1604'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='has_trees',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='survey',
            name='is_left_side',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='survey',
            name='is_mapped_in_blockface_polyline_direction',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='survey',
            name='quit_reason',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tree',
            name='circumference',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tree',
            name='curb_location',
            field=models.CharField(default='OnCurb', max_length=25, choices=[('OnCurb', 'Tree bed is along the curb'), ('OffsetFromCurb', 'Tree bed is offset from the curb')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tree',
            name='distance_to_end',
            field=models.PositiveIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tree',
            name='distance_to_tree',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tree',
            name='guards',
            field=models.CharField(blank=True, max_length=15, choices=[('None', 'No guard installed'), ('Helpful', 'Helpful guard installed'), ('Harmful', 'Harmful guard installed'), ('Unsure', 'Unsure if guard is helpful or harmful')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tree',
            name='health',
            field=models.CharField(blank=True, max_length=15, choices=[('Good', 'Good'), ('Fair', 'Fair'), ('Poor', 'Poor')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tree',
            name='problems',
            field=models.CharField(max_length=130, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tree',
            name='sidewalk_damage',
            field=models.CharField(blank=True, max_length=15, choices=[('NoDamage', 'No damage is seen'), ('Damage', 'Cracks or raised sidewalk seen')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tree',
            name='species_certainty',
            field=models.CharField(blank=True, max_length=15, choices=[('Yes', 'Yes'), ('No', 'No'), ('Maybe', 'Maybe')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tree',
            name='status',
            field=models.CharField(default='Alive', max_length=15, choices=[('Alive', 'Tree is alive'), ('Dead', 'Tree is dead'), ('Stump', 'Stump [<24"]')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tree',
            name='stewardship',
            field=models.CharField(blank=True, max_length=15, choices=[('None', 'Zero'), ('1or2', 'One to two'), ('3or4', 'Three to four'), ('4orMore', 'More than four')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='species',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='survey.Species', null=True),
            preserve_default=True,
        ),
    ]
