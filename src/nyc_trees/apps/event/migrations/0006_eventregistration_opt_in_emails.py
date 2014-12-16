# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0005_auto_20141218_1351'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventregistration',
            name='opt_in_emails',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
