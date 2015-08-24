# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0028_update_layoutboxes_20150529_1328'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='submit_comment',
            field=models.TextField(help_text='Description of why survey was remapped or submitted for review', blank=True),
            preserve_default=True,
        ),
    ]
