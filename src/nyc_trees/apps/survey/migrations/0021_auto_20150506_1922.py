# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0020_auto_20150505_1155'),
    ]

    operations = [
        migrations.CreateModel(
            name='Borough',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(help_text='Time when row was created', auto_now_add=True)),
                ('updated_at', models.DateTimeField(help_text='Time when row was last updated', auto_now=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
                ('name', models.CharField(max_length=32)),
                ('code', models.IntegerField(unique=True, db_index=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NeighborhoodTabulationArea',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(help_text='Time when row was created', auto_now_add=True)),
                ('updated_at', models.DateTimeField(help_text='Time when row was last updated', auto_now=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
                ('name', models.CharField(max_length=75)),
                ('code', models.CharField(unique=True, max_length=4, db_index=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='blockface',
            name='borough',
            field=models.ForeignKey(to='survey.Borough', help_text='The borough containing this blockface', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='blockface',
            name='nta',
            field=models.ForeignKey(to='survey.NeighborhoodTabulationArea', help_text='The neighborhood tabulation area containing this blockface', null=True),
            preserve_default=True,
        ),
    ]
