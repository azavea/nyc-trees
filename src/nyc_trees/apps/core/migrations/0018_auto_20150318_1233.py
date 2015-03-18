# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import apps.core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_group_affiliation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='image',
            field=models.ImageField(null=True, upload_to=apps.core.models._generate_image_filename, blank=True),
            preserve_default=True,
        ),
    ]
