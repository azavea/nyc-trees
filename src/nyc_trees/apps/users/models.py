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
    description - string
    badge - path for a static image file
    progress - a function which takes a user and returns a number from 0-100
    """
    def __init__(self, description, badge, progress):
        assert isinstance(description, basestring)
        assert isinstance(badge, basestring)
        assert hasattr(progress, '__call__')

        self.description = description
        self.badge = badge
        self.progress = progress


# TODO: These are just for testing purposes, we are waiting for real data
achievements = OrderedDict([
    ('Professor Tree', AchievementDefinition(
        description='Finish Training',
        badge='img/placeholder.gif',
        progress=lambda user: 100 if user.online_training_complete else 0
    )),
    ('Groupie', AchievementDefinition(
        description='Join 10 Groups',
        badge='img/placeholder.gif',
        progress=lambda user: min(100, user.group_set.count() * 10)
    )),
])

achievement_choices = [(name, achievement_def.description)
                       for name, achievement_def in achievements.iteritems()]


class Follow(NycModel, models.Model):
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)


class TrustedMapper(NycModel, models.Model):
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)


class TrainingResult(NycModel, models.Model):
    user = models.ForeignKey(User)
    module_name = models.CharField(max_length=255)
    score = models.IntegerField(null=True)


class Achievement(NycModel, models.Model):
    user = models.ForeignKey(User)
    achievement_name = models.CharField(max_length=100,
                                        choices=achievement_choices)

    unique_together = ("user", "achievement_name")
