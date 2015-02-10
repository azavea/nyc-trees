# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20150113_1210'),
    ]

    operations = [
        migrations.AddField(
            model_name='trustedmapper',
            name='is_approved',
            field=models.NullBooleanField(),
            preserve_default=True,
        ),
    ]
