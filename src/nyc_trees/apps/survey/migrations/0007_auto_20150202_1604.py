# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0006_auto_20150113_1533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='territory',
            name='blockface',
            field=models.OneToOneField(to='survey.Blockface'),
            preserve_default=True,
        ),
    ]
