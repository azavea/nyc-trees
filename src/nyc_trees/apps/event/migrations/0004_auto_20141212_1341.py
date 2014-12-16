# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0003_auto_20141211_1702'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='event',
            unique_together=set([('group', 'slug'), ('group', 'title')]),
        ),
    ]
