# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20141226_1720'),
    ]

    operations = [
        migrations.RenameField(
            model_name='group',
            old_name='contact_info',
            new_name='contact_name',
        ),
    ]
