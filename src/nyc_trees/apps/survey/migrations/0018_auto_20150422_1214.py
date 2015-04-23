# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0017_auto_20150415_1419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blockface',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
            preserve_default=True,
        ),
    ]
