# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0005_auto_20150106_1825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blockfacereservation',
            name='canceled_at',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='survey',
            name='teammate',
            field=models.ForeignKey(related_name='surveys_as_teammate', on_delete=django.db.models.deletion.PROTECT, blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
