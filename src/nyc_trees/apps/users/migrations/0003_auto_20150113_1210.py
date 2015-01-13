# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20141209_1629'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='trustedmapper',
            unique_together=set([('user', 'group')]),
        ),
    ]
