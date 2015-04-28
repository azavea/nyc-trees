# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='territory_updated_at',
            field=models.DateTimeField(db_index=True, null=True, editable=False, blank=True),
            preserve_default=True,
        ),
    ]
