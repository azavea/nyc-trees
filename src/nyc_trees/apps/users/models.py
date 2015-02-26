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
    description - string - description of the achievement requirements
    badge - path for a static image file
    progress - a function which takes a user and returns a number from 0-100
    """
    def __init__(self, name, description, badge, progress):
        assert isinstance(name, basestring)
        assert isinstance(description, basestring)
        assert isinstance(badge, basestring)
        assert hasattr(progress, '__call__')

        self.name = name
        self.description = description
        self.badge = badge
        self.progress = progress

    FINISH_TRAINING = 0
    JOIN_10_GROUPS = 1


# TODO: These are just for testing purposes, we are waiting for real data
achievements = OrderedDict([
    (AchievementDefinition.FINISH_TRAINING, AchievementDefinition(
        name='Professor Tree',
        description='Finish Training',
        badge='img/placeholder.gif',
        progress=lambda user: 100 if user.online_training_complete else 0
    )),
    (AchievementDefinition.JOIN_10_GROUPS, AchievementDefinition(
        name='Groupie',
        description='Join 10 Groups',
        badge='img/placeholder.gif',
        progress=lambda user: min(100, user.group_set.count() * 10)
    )),
])

achievement_choices = [(key, achievement_def.name)
                       for key, achievement_def in achievements.iteritems()]


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
