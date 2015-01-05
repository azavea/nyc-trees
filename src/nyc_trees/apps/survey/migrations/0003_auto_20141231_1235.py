# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0002_auto_20141204_1024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='territory',
            name='blockface',
            field=models.ForeignKey(to='survey.Blockface', unique=True),
        ),
    ]
