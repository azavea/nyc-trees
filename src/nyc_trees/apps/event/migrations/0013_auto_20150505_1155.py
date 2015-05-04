# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0012_auto_20150424_1705'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='address',
            field=models.CharField(help_text='Approximate address of meeting location', max_length=1000),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='begins_at',
            field=models.DateTimeField(help_text='When the event starts'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='contact_email',
            field=models.EmailField(help_text='Email address of contact person', max_length=75, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='contact_name',
            field=models.CharField(default='', help_text='Name of contact person', max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='created_at',
            field=models.DateTimeField(help_text='Time when row was created', auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.TextField(default='', help_text='Description of event, for display', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='ends_at',
            field=models.DateTimeField(help_text='When the event ends'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Group', help_text='Group sponsoring the event'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='includes_training',
            field=models.BooleanField(default=False, help_text='Is this a training event?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='is_canceled',
            field=models.BooleanField(default=False, help_text='Has this event been canceled?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='is_private',
            field=models.BooleanField(default=False, help_text='Is this a private event?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(help_text='Location displayed on event maps', srid=4326),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='location_description',
            field=models.TextField(default='', help_text='How to find the event meeting location', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='map_pdf_filename',
            field=models.CharField(default='', help_text='S3 file path of event map PDF', max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='max_attendees',
            field=models.IntegerField(help_text='Maximum number of people allowed to RSVP'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='slug',
            field=models.SlugField(help_text='Short name used in URLs', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='title',
            field=models.CharField(help_text='Name of event, for display', max_length=255, validators=[django.core.validators.RegexValidator('[\\w][\\w\\s]+')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='updated_at',
            field=models.DateTimeField(help_text='Time when row was last updated', auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventregistration',
            name='created_at',
            field=models.DateTimeField(help_text='Time when row was created', auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventregistration',
            name='did_attend',
            field=models.BooleanField(default=False, help_text='Was user  checked in to event?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventregistration',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='event.Event', help_text='ID of event registered for'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventregistration',
            name='opt_in_emails',
            field=models.BooleanField(default=True, help_text='Should user receive emails for this event?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventregistration',
            name='updated_at',
            field=models.DateTimeField(help_text='Time when row was last updated', auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventregistration',
            name='user',
            field=models.ForeignKey(help_text='ID of user registering for event', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
