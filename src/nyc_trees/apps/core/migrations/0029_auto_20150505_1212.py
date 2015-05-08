# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.conf import settings
import apps.core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_user_survey_geolocate_help_shown'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='admin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to=settings.AUTH_USER_MODEL, help_text='ID of user who is the group administrator', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='group',
            name='affiliation',
            field=models.CharField(default='', help_text='Name of organization affiliated with group', max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='group',
            name='allows_individual_mappers',
            field=models.BooleanField(default=False, help_text="Can users request permission to map in group's territory?"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='group',
            name='border',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(help_text='Map area associated with group', srid=4326, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='group',
            name='contact_email',
            field=models.EmailField(help_text='Email address of contact person for group', max_length=75, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='group',
            name='contact_name',
            field=models.CharField(default='', help_text='Name of contact person for group', max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='group',
            name='contact_url',
            field=models.URLField(help_text="URL of group's external website", null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='group',
            name='created_at',
            field=models.DateTimeField(help_text='Time when row was created', auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(default='', help_text='Description of group, for display', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='group',
            name='image',
            field=models.ImageField(help_text='S3 path of uploaded group logo', null=True, upload_to=apps.core.models._generate_image_filename, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='group',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Should this group be listed on the "Groups" page?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='group',
            name='name',
            field=models.CharField(help_text='Name of group, for display', unique=True, max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(help_text='Short name for group, used in URLs', unique=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='group',
            name='territory_updated_at',
            field=models.DateTimeField(help_text="Time when group's block edge assignments were last updated", null=True, editable=False, db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='group',
            name='updated_at',
            field=models.DateTimeField(help_text='Time when row was last updated', auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='achievements_are_public',
            field=models.BooleanField(default=False, help_text="Can other users see this user's achievements?"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='contributions_are_public',
            field=models.BooleanField(default=False, help_text="Can other users see this user's mapping statistics?"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(help_text='Time when row was created', auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='field_training_complete',
            field=models.BooleanField(default=False, help_text='Was user checked in to a mapping event?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='group_follows_are_public',
            field=models.BooleanField(default=False, help_text='Can other users see which groups this user is following?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='individual_mapper',
            field=models.NullBooleanField(help_text='Can user reserve and map block edges outside of events?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='is_minor',
            field=models.BooleanField(default=False, help_text='Is user 13 years old or under?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='opt_in_stewardship_info',
            field=models.BooleanField(default=False, help_text='User chose to receive information from Parks'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='profile_is_public',
            field=models.BooleanField(default=False, help_text="Can other users see this user's profile?"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='progress_page_help_shown',
            field=models.BooleanField(default=False, help_text='Seen help text on Progress page?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='real_name_is_public',
            field=models.BooleanField(default=False, help_text="Can other users see this user's real name?"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='referrer_311',
            field=models.BooleanField(default=False, help_text='Did user learn of site via 311?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='referrer_ad',
            field=models.CharField(default='', help_text='How user learned of site (ad sources)', max_length=25, blank=True, choices=[('bus', 'Bus Poster'), ('subway', 'Subway Poster'), ('tv', 'Television'), ('radio', 'Radio'), ('website', 'Website')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='referrer_friend',
            field=models.BooleanField(default=False, help_text='Did user learn of site via a friend?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='referrer_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='core.Group', help_text='How user learned of site (census group sources)', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='referrer_other',
            field=models.CharField(default='', help_text='How user learned of site (other sources)', max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='referrer_parks',
            field=models.CharField(default='', help_text='How user learned of site (Parks sources)', max_length=25, blank=True, choices=[('website', 'Website'), ('newsletter', 'Newsletter'), ('employee', 'I am a Parks employee')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='referrer_social_media',
            field=models.BooleanField(default=False, help_text='Did user learn of site via social media?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='requested_individual_mapping_at',
            field=models.DateTimeField(help_text='Time when user requested individual mapper status', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='reservation_ids_in_map_pdf',
            field=models.TextField(default='', help_text='IDs of reservations in PDF map', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='reservations_map_pdf_filename',
            field=models.CharField(default='', help_text='S3 file path of reservations map PDF', max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='reservations_page_help_shown',
            field=models.BooleanField(default=False, help_text='Seen help text on Reservations page?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='survey_geolocate_help_shown',
            field=models.BooleanField(default=False, help_text='Seen geolocation help text on Survey page?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='training_finished_getting_started',
            field=models.BooleanField(default=False, help_text='"Getting Started" training section completed?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='training_finished_groups_to_follow',
            field=models.BooleanField(default=False, help_text='Seen invitation to follow groups?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='training_finished_intro_quiz',
            field=models.BooleanField(default=False, help_text='Intro Quiz completed?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='training_finished_the_mapping_method',
            field=models.BooleanField(default=False, help_text='"Mapping Method" training section completed?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='training_finished_tree_data',
            field=models.BooleanField(default=False, help_text='"Tree Data" training section completed?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='training_finished_tree_surroundings',
            field=models.BooleanField(default=False, help_text='"Tree Surroundings" training section completed?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='training_finished_wrapping_up',
            field=models.BooleanField(default=False, help_text='"Wrapping Up" training section completed?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='updated_at',
            field=models.DateTimeField(help_text='Time when row was last updated', auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='zip_code',
            field=models.CharField(default='', help_text="User's ZIP Code", max_length=25, blank=True),
            preserve_default=True,
        ),
    ]
