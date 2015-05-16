# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_auto_20150506_1635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='requested_individual_mapping_at',
            field=models.DateTimeField(help_text='Time when user requested independent mapper status', null=True, blank=True),
            preserve_default=True,
        ),
    ]
