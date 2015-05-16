# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0025_auto_20150513_1343'),
    ]

    def delete_ntas(apps, schema_editor):
        NTA = apps.get_model('survey', 'NeighborhoodTabulationArea')
        Blockface = apps.get_model('survey', 'Blockface')

        # Delete all pointers to NTAs from the blockface table.
        # They will be reassigned by a management command
        Blockface.objects.update(nta=None)
        NTA.objects.filter(code__in=[
            'MN99', 'BK99', 'BX99', 'QN99', 'SI99', 'QN98', 'BX98']).delete()

    def noop(apps, schema_editor):
        pass

    operations = [
        migrations.RunPython(delete_ntas, noop)
    ]
