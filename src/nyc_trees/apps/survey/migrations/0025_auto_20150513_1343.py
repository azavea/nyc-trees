# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db import migrations


_halesia_kwargs = json.loads("""{
"pk": 60,
"species_code": "HACA",
"scientific_name": "Halesia carolina",
"forms_id": 39541,
"common_name": "Silverbell",
"cultivar": ""
}""")


def delete_halesia(apps, schema_editor):
    Species = apps.get_model('survey', 'Species')
    try:
        Species.objects.get(**_halesia_kwargs).delete()
    except Species.DoesNotExist:
        pass


def create_halesia(apps, schema_editor):
    Species = apps.get_model('survey', 'Species')
    Species.objects.create(**_halesia_kwargs)


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0024_merge'),
    ]

    operations = [
        migrations.RunPython(delete_halesia, create_halesia),
    ]
