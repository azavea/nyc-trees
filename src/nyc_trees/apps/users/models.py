# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.db import models

from apps.core.models import User, Group


class Follow(models.Model):
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TrustedMapper(models.Model):
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TrainingResult(models.Model):
    user = models.ForeignKey(User)
    module_name = models.CharField(max_length=255)
    score = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
