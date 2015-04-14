# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0014_blockfacereservation_reminder_sent_at'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='species',
            options={'ordering': ['common_name', 'scientific_name', 'cultivar']},
        ),
    ]
