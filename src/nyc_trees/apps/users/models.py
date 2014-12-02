# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.db import models

from apps.core.models import User, Group

from libs.mixins import NycModel


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
