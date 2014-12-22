# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20141202_1400'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='opt_in_events_info',
        ),
    ]
