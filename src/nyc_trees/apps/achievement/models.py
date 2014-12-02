# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.db import models

from apps.core.models import User

from libs.mixins import NycModel


class AchievementDefinition(NycModel, models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(default='', blank=True)
    badge_image = models.ImageField(null=True)


class Achievement(NycModel, models.Model):
    user = models.ForeignKey(User)
    achievement_definition = models.ForeignKey(AchievementDefinition)
