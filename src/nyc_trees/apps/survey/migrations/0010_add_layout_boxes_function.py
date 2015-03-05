# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.db import models, migrations

_LAYOUTBOXES_FILE = os.path.join(os.path.dirname(__file__), 'layoutBoxes.sql')

with open(_LAYOUTBOXES_FILE, 'r') as f:
    _CREATE_LAYOUTBOXES = f.read()

_DROP_LAYOUTBOXES = """
DROP FUNCTION IF EXISTS layoutBoxes(line geometry, left_side boolean,
dist float8[], len float8[], width float8[], off float8[])
"""

class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0010_auto_20150305_1341'),
    ]

    operations = [
        migrations.RunSQL(sql=_CREATE_LAYOUTBOXES,
                          reverse_sql=_DROP_LAYOUTBOXES),
    ]
