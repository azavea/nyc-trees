# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0020_auto_20150505_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blockfacereservation',
            name='updated_at',
            field=models.DateTimeField(help_text='Time when row was last updated', auto_now=True, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='survey',
            name='updated_at',
            field=models.DateTimeField(help_text='Time when row was last updated', auto_now=True, db_index=True),
            preserve_default=True,
        ),
    ]
