# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20141226_1722'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='referrer_311',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='referrer_ad',
            field=models.CharField(default='', max_length=25, blank=True, choices=[('bus', 'Bus Poster'), ('subway', 'Subway Poster'), ('tv', 'Television'), ('radio', 'Radio'), ('website', 'Website')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='referrer_friend',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='referrer_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='core.Group', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='referrer_other',
            field=models.CharField(default='', max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='referrer_parks',
            field=models.CharField(default='', max_length=25, blank=True, choices=[('website', 'Website'), ('newsletter', 'Newsletter'), ('employee', 'I am a Parks employee')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='referrer_social_media',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='zip_code',
            field=models.CharField(default='', max_length=25, blank=True),
            preserve_default=True,
        ),
    ]
