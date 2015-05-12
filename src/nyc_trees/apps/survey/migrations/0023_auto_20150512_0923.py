# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0022_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blockface',
            name='borough',
            field=models.ForeignKey(blank=True, to='survey.Borough', help_text='The borough containing this blockface', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blockface',
            name='nta',
            field=models.ForeignKey(blank=True, to='survey.NeighborhoodTabulationArea', help_text='The neighborhood tabulation area containing this blockface', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='borough',
            name='code',
            field=models.IntegerField(unique=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='neighborhoodtabulationarea',
            name='code',
            field=models.CharField(unique=True, max_length=4),
            preserve_default=True,
        ),
    ]
