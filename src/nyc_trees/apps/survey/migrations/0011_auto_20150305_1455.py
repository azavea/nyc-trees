# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0010_auto_20150305_1341'),
    ]

    operations = [
        migrations.AddField(
            model_name='species',
            name='common_name',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='species',
            name='cultivar',
            field=models.CharField(max_length=100, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='species',
            name='forms_id',
            field=models.CharField(default='', max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='species',
            name='scientific_name',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='species',
            name='species_code',
            field=models.CharField(default='', max_length=10),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='species',
            unique_together=set([('scientific_name', 'cultivar', 'common_name')]),
        ),
        migrations.RemoveField(
            model_name='species',
            name='name',
        ),
    ]
