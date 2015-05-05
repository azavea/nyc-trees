# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import apps.users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20150422_1649'),
    ]

    operations = [
        migrations.AlterField(
            model_name='achievement',
            name='achievement_id',
            field=models.IntegerField(help_text=apps.users.models.achievement_help_text, choices=[(1, 'In Pursuit of Mappiness'), (0, 'Ready, Set, Roll'), (2, 'Treerifically Trained'), (3, 'Counter Cultured'), (4, 'Rolling Revolutionary'), (5, 'Mapping Machine'), (6, 'Sprout Mapper'), (7, 'Seedling Mapper'), (8, 'Sapling Mapper'), (9, 'Mayoral Mapper')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='achievement',
            name='created_at',
            field=models.DateTimeField(help_text='Time when row was created', auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='achievement',
            name='updated_at',
            field=models.DateTimeField(help_text='Time when row was last updated', auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='achievement',
            name='user',
            field=models.ForeignKey(help_text='ID of user who achieved the achievement', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='follow',
            name='created_at',
            field=models.DateTimeField(help_text='Time when row was created', auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='follow',
            name='group',
            field=models.ForeignKey(help_text='ID of group being followed', to='core.Group'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='follow',
            name='updated_at',
            field=models.DateTimeField(help_text='Time when row was last updated', auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='follow',
            name='user',
            field=models.ForeignKey(help_text='ID of user following group', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trainingresult',
            name='created_at',
            field=models.DateTimeField(help_text='Time when row was created', auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trainingresult',
            name='module_name',
            field=models.CharField(help_text='Name of quiz', max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trainingresult',
            name='score',
            field=models.IntegerField(help_text='Number of questions answered correctly', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trainingresult',
            name='updated_at',
            field=models.DateTimeField(help_text='Time when row was last updated', auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trainingresult',
            name='user',
            field=models.ForeignKey(help_text='ID of user answering quiz questions', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trustedmapper',
            name='created_at',
            field=models.DateTimeField(help_text='Time when row was created', auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trustedmapper',
            name='group',
            field=models.ForeignKey(help_text='ID of group granting mapping permission', to='core.Group'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trustedmapper',
            name='is_approved',
            field=models.NullBooleanField(help_text='Has mapping permission been granted?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trustedmapper',
            name='updated_at',
            field=models.DateTimeField(help_text='Time when row was last updated', auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trustedmapper',
            name='user',
            field=models.ForeignKey(help_text='ID of user requesting mapping permission', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
