# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0029_survey_submit_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='survey',
            name='submit_comment',
            field=models.TextField(default='', help_text='Description of why survey was remapped or submitted for review', blank=True),
            preserve_default=False,
        ),
    ]
