# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20150408_1216'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['username']},
        ),
    ]
