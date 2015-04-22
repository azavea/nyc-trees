# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from collections import OrderedDict

from django.db import models

from apps.core.models import User, Group

from libs.mixins import NycModel


class AchievementDefinition(object):
    """A class representing an achievment definition
    name - string - title of the achievement
    description - requirements (after achievement)
    description_future - requirements (before achievement)
    badge - path for a static image file
    achieved - a function which takes a user and returns a boolean
    """
    def __init__(self, name, description, description_achieved, badge,
                 achieved):
        assert isinstance(name, basestring)
        assert isinstance(description, basestring)
        assert isinstance(description_achieved, basestring)
        assert isinstance(badge, basestring)
        assert callable(achieved)

        self.name = name
        self.description = description
        self.description_achieved = description_achieved
        self.badge = badge
        self.achieved = achieved

    ONLINE_TRAINING = 0
    FOLLOW_GROUPS = 1
    TRAINING_EVENT = 2
    MAPPING_EVENT = 3
    MAP_50 = 4
    MAP_100 = 5
    MAP_200 = 6
    MAP_400 = 7
    MAP_1000 = 8
    MAP_MOST = 9


achievements = OrderedDict([
    (AchievementDefinition.FOLLOW_GROUPS, AchievementDefinition(
        name='In Pursuit of Mappiness',
        description='Follow 5 Groups',
        description_achieved='Followed 5 Groups',
        badge='img/badges/ic_badge_follow.png',
        achieved=lambda user: Follow.objects.filter(user=user).count() >= 5
    )),
    (AchievementDefinition.ONLINE_TRAINING, AchievementDefinition(
        name='Ready, Set, Roll',
        description='Finish Online Training',
        description_achieved='Finished Online Training',
        badge='img/badges/ic_badge_online_training.png',
        achieved=lambda user: user.online_training_complete
    )),
    (AchievementDefinition.TRAINING_EVENT, AchievementDefinition(
        name='Certified Mapper',
        description='Attend a Training Event',
        description_achieved='Attended a Training Event',
        badge='img/badges/ic_badge_training_event.png',
        achieved=lambda user: user.field_training_complete
    )),
    (AchievementDefinition.MAPPING_EVENT, AchievementDefinition(
        name='Free Mapper',
        description='Attend a Mapping Event',
        description_achieved='Attended a Mapping Event',
        badge='img/badges/ic_badge_mapping_event.png',
        achieved=lambda user: user.attended_at_least_two_events()
    )),
    (AchievementDefinition.MAP_50, AchievementDefinition(
        name='Map 50 Block Edges',
        description='Map 50 Block Edges',
        description_achieved='Mapped 50 Block Edges',
        badge='img/badges/ic_badge_map_50.png',
        achieved=lambda user: user.blocks_mapped_count >= 50
    )),
    (AchievementDefinition.MAP_100, AchievementDefinition(
        name='Map 100 Block Edges',
        description='Map 100 Block Edges',
        description_achieved='Mapped 100 Block Edges',
        badge='img/badges/ic_badge_map_100.png',
        achieved=lambda user: user.blocks_mapped_count >= 100
    )),
    (AchievementDefinition.MAP_200, AchievementDefinition(
        name='Map 200 Block Edges',
        description='Map 200 Block Edges',
        description_achieved='Mapped 200 Block Edges',
        badge='img/badges/ic_badge_map_200.png',
        achieved=lambda user: user.blocks_mapped_count >= 200
    )),
    (AchievementDefinition.MAP_400, AchievementDefinition(
        name='Map 400 Block Edges',
        description='Map 400 Block Edges',
        description_achieved='Mapped 400 Block Edges',
        badge='img/badges/ic_badge_map_400.png',
        achieved=lambda user: user.blocks_mapped_count >= 400
    )),
    (AchievementDefinition.MAP_1000, AchievementDefinition(
        name='Map 1000 Block Edges',
        description='Map 1000 Block Edges',
        description_achieved='Mapped 1000 Block Edges',
        badge='img/badges/ic_badge_map_1000.png',
        achieved=lambda user: user.blocks_mapped_count >= 1000
    )),
    (AchievementDefinition.MAP_MOST, AchievementDefinition(
        name='Map the Most Block Edges in NYC',
        description='Map the Most Block Edges in NYC',
        description_achieved='Mapped the Most Block Edges in NYC',
        badge='img/badges/ic_badge_top_mapper.png',
        achieved=lambda user: False  # doesn't need to be live updated
    )),
])


achievement_choices = [(key, achievement_def.name)
                       for key, achievement_def in achievements.iteritems()]


def update_achievements(user):
    achieved_ids = set([a.achievement_id
                        for a in user.achievement_set.all()])

    for id, definition in achievements.iteritems():
        if id not in achieved_ids and definition.achieved(user):
            a = Achievement(user=user, achievement_id=id)
            a.save()


class Follow(NycModel, models.Model):
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)

    def __unicode__(self):
        return '%s -> %s' % (self.user, self.group)


class TrustedMapper(NycModel, models.Model):
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    is_approved = models.NullBooleanField()

    def __unicode__(self):
        return '%s -> %s' % (self.user, self.group)

    class Meta:
        unique_together = ("user", "group")


class TrainingResult(NycModel, models.Model):
    user = models.ForeignKey(User)
    module_name = models.CharField(max_length=255)
    score = models.IntegerField(null=True)


class Achievement(NycModel, models.Model):
    user = models.ForeignKey(User)
    achievement_id = models.IntegerField(choices=achievement_choices)

    class Meta:
        unique_together = ("user", "achievement_id")
