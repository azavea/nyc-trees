# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0019_auto_20150501_0954'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blockface',
            name='created_at',
            field=models.DateTimeField(help_text='Time when row was created', auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blockface',
            name='expert_required',
            field=models.BooleanField(default=False, help_text='Is an expert required to survey this blockface?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blockface',
            name='geom',
            field=django.contrib.gis.db.models.fields.MultiLineStringField(help_text='Coordinates of blockface polyline', srid=4326),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blockface',
            name='is_available',
            field=models.BooleanField(default=True, help_text='Is blockface available for surveying?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blockface',
            name='source',
            field=models.CharField(default='unknown', help_text='Source for blockface data (borough name)', max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blockface',
            name='updated_at',
            field=models.DateTimeField(help_text='Time when row was last updated', auto_now=True, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blockfacereservation',
            name='blockface',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='survey.Blockface', help_text='ID of blockface reserved'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blockfacereservation',
            name='canceled_at',
            field=models.DateTimeField(help_text='Cancellation time [if reservation was canceled]', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blockfacereservation',
            name='created_at',
            field=models.DateTimeField(help_text='Time when row was created', auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blockfacereservation',
            name='expires_at',
            field=models.DateTimeField(help_text='Expiration time for this reservation'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blockfacereservation',
            name='is_mapping_with_paper',
            field=models.BooleanField(default=False, help_text='Does user plan to survey using the paper form?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blockfacereservation',
            name='reminder_sent_at',
            field=models.DateTimeField(help_text='Time expiration reminder was emailed', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blockfacereservation',
            name='updated_at',
            field=models.DateTimeField(help_text='Time when row was last updated', auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blockfacereservation',
            name='user',
            field=models.ForeignKey(help_text='ID of user reserving blockface', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='species',
            name='common_name',
            field=models.CharField(help_text='Common name for species, e.g. "Red Maple"', max_length=100),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='species',
            name='created_at',
            field=models.DateTimeField(help_text='Time when row was created', auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='species',
            name='cultivar',
            field=models.CharField(help_text='Further qualifies scientific name', max_length=100, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='species',
            name='forms_id',
            field=models.CharField(help_text='ID from original data source', max_length=10),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='species',
            name='scientific_name',
            field=models.CharField(help_text='Scientific name for species, e.g. "Acer Rubrum"', max_length=100),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='species',
            name='species_code',
            field=models.CharField(help_text='Species code from original data source', max_length=10),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='species',
            name='updated_at',
            field=models.DateTimeField(help_text='Time when row was last updated', auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='survey',
            name='blockface',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='survey.Blockface', help_text='ID of blockface surveyed'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='survey',
            name='created_at',
            field=models.DateTimeField(help_text='Time when row was created', auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='survey',
            name='has_trees',
            field=models.BooleanField(help_text='Did blockface contain any trees?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='survey',
            name='is_flagged',
            field=models.BooleanField(default=False, help_text='Did user request a review for this survey?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='survey',
            name='is_left_side',
            field=models.BooleanField(help_text='Was left side of block surveyed?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='survey',
            name='is_mapped_in_blockface_polyline_direction',
            field=models.BooleanField(help_text='Does survey begin at first point of blockface polyline?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='survey',
            name='quit_reason',
            field=models.TextField(help_text='Description of why survey was abandoned', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='survey',
            name='teammate',
            field=models.ForeignKey(related_name='surveys_as_teammate', on_delete=django.db.models.deletion.PROTECT, blank=True, to=settings.AUTH_USER_MODEL, help_text='ID of user helping with survey', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='survey',
            name='updated_at',
            field=models.DateTimeField(help_text='Time when row was last updated', auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='survey',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, help_text='ID of user performing survey'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='territory',
            name='blockface',
            field=models.OneToOneField(to='survey.Blockface', help_text='ID of blockface'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='territory',
            name='created_at',
            field=models.DateTimeField(help_text='Time when row was created', auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='territory',
            name='group',
            field=models.ForeignKey(help_text='ID of group responsible for surveying blockface', to='core.Group'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='territory',
            name='updated_at',
            field=models.DateTimeField(help_text='Time when row was last updated', auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='circumference',
            field=models.PositiveIntegerField(help_text='Measured circumference (inches) [if not a stump]', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='created_at',
            field=models.DateTimeField(help_text='Time when row was created', auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='curb_location',
            field=models.CharField(help_text='Location of tree bed', max_length=25, choices=[('OnCurb', 'Along the curb'), ('OffsetFromCurb', 'Offset from the curb')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='distance_to_end',
            field=models.FloatField(help_text='Measured distance to end of block (feet) [only if final tree in survey]', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='distance_to_tree',
            field=models.FloatField(help_text='Measured distance to tree (feet)'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='guards',
            field=models.CharField(blank=True, help_text='Status of tree guards [if alive]', max_length=15, choices=[('None', 'Not installed'), ('Helpful', 'Helpful'), ('Harmful', 'Harmful'), ('Unsure', 'Unsure')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='health',
            field=models.CharField(blank=True, help_text='Perception of tree health [if alive]', max_length=15, choices=[('Good', 'Good'), ('Fair', 'Fair'), ('Poor', 'Poor')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='problems',
            field=models.CharField(help_text='Observed problems (comma-separated strings) [if alive]', max_length=130, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='sidewalk_damage',
            field=models.CharField(blank=True, help_text='Observed sidewalk damage [if alive]', max_length=15, choices=[('NoDamage', 'No damage'), ('Damage', 'Cracks or raised')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='species',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='survey.Species', help_text='ID of tree species', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='species_certainty',
            field=models.CharField(blank=True, help_text='How certain is user of species? [if alive]', max_length=15, choices=[('Yes', 'Yes'), ('No', 'No'), ('Maybe', 'Maybe')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='status',
            field=models.CharField(help_text='Is this tree alive, dead, or a stump?', max_length=15, choices=[('Alive', 'Tree is alive'), ('Dead', 'Tree is dead'), ('Stump', 'Stump (<24" tall)')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='stewardship',
            field=models.CharField(blank=True, help_text='Number of observed stewardship practices [if alive]', max_length=15, choices=[('None', 'Zero'), ('1or2', '1-2'), ('3or4', '3-4'), ('4orMore', '4+')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='stump_diameter',
            field=models.PositiveIntegerField(help_text='Measured diameter (inches) [if a stump]', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='survey',
            field=models.ForeignKey(help_text='ID of survey containing this tree', to='survey.Survey'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tree',
            name='updated_at',
            field=models.DateTimeField(help_text='Time when row was last updated', auto_now=True),
            preserve_default=True,
        ),
    ]
