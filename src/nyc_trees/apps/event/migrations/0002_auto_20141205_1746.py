# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='url_name',
        ),
        migrations.AddField(
            model_name='event',
            name='slug',
            field=models.SlugField(default='', blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='title',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='event',
            unique_together=set([('group', 'slug')]),
        ),
    ]
