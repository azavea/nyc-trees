# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0013_auto_20150309_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='blockfacereservation',
            name='reminder_sent_at',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
