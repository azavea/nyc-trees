# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0006_eventregistration_opt_in_emails'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='contact_info',
            new_name='contact_name',
        ),
    ]
