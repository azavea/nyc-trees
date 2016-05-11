# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from apps.core.models import User
from apps.users.models import achievements, AchievementDefinition, Achievement


untrained_achievements = {
    AchievementDefinition.ONLINE_TRAINING, AchievementDefinition.FOLLOW_GROUPS}


def update_inactive_achievements(user, is_untrained):
    achieved_ids = set([a.achievement_id
                        for a in user.achievement_set.all()])

    for id, definition in achievements.iteritems():
        if is_untrained and id not in untrained_achievements:
            continue

        if ((id not in achieved_ids and not definition.active and
             definition.achieved(user))):
            a = Achievement(user=user, achievement_id=id)
            a.save()


def record_achievements(apps, schema_editor):
    # We use the real user model instead of the migration model in order to use
    # its helper methods
    users = User.objects.select_related('achievements')

    untrained = users.filter(field_training_complete=False)
    trained = users.filter(field_training_complete=True)

    for user in untrained:
        update_inactive_achievements(user, True)

    for user in trained:
        update_inactive_achievements(user, False)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_auto_20160415_1550'),
        ('core', '0031_auto_20150513_1536'),
    ]

    operations = [
        migrations.RunPython(record_achievements, noop)
    ]
