# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0004_auto_20141212_1341'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='eventregistration',
            unique_together=set([('user', 'event')]),
        ),
    ]
