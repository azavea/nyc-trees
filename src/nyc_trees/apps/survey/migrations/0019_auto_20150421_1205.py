# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0018_blockface_latest_survey'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blockface',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
            preserve_default=True,
        ),
    ]
