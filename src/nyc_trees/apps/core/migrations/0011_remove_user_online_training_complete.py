# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20150121_1059'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='online_training_complete',
        ),
    ]
