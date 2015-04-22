# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0018_auto_20150422_1214'),
    ]

    operations = [
        migrations.AddField(
            model_name='blockface',
            name='latest_survey',
            field=models.ForeignKey(related_name='surveyed_blockface', on_delete=django.db.models.deletion.PROTECT, blank=True, to='survey.Survey', null=True),
            preserve_default=True,
        ),
    ]
