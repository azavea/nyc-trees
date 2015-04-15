# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0016_blockface_source'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='species',
            options={'ordering': ['common_name', 'scientific_name', 'cultivar'], 'verbose_name_plural': 'Species'},
        ),
        migrations.AlterModelOptions(
            name='territory',
            options={'verbose_name_plural': 'Territories'},
        ),
    ]
