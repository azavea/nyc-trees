# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.db import models, migrations


_LAYOUTBOXES_FILE = os.path.join(os.path.dirname(__file__), 'layoutBoxes.sql')

with open(_LAYOUTBOXES_FILE, 'r') as f:
    _CREATE_LAYOUTBOXES = f.read()


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0021_auto_20150506_1406'),
    ]

    operations = [
        # The reverse is a no-op, but Django makes us provide valid SQL
        migrations.RunSQL(sql=_CREATE_LAYOUTBOXES, reverse_sql="SELECT 1;")
    ]
