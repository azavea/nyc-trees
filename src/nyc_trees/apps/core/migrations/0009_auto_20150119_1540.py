# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20141226_1722'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='training_finished_getting_started',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='training_finished_the_mapping_method',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='training_finished_tree_data',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='training_finished_tree_surroundings',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='visited_training_page_groups_to_follow',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
