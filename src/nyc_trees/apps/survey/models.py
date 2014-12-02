# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.gis.db import models

from apps.core.models import User, Group

from libs.mixins import NycModel


class Blockface(NycModel, models.Model):
    geom = models.LineStringField(srid=3857,
                                  db_column='the_geom_webmercator')
    is_available = models.BooleanField(default=True)


class Territory(NycModel, models.Model):
    group = models.ForeignKey(Group)
    blockface = models.ForeignKey(Blockface)


class Survey(NycModel, models.Model):
    # We do not anticipate deleting a Blockface, but we definitely
    # should not allow it to be deleted if there is a related Survey
    blockface = models.ForeignKey(Blockface, on_delete=models.PROTECT)
    # We do not want to lose survey data by allowing the deletion of
    # a User object to automatically cascade and delete the Survey
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    teammate = models.ForeignKey(User, null=True, on_delete=models.PROTECT,
                                 related_name='surveys_as_teammate')
    is_flagged = models.BooleanField(default=False)


class Tree(NycModel, models.Model):
    survey = models.ForeignKey(Survey)


class BlockfaceReservation(NycModel, models.Model):
    user = models.ForeignKey(User)
    # We do not plan on Blockface records being deleted, but we should
    # make sure that a Blockface that has been reserved cannot be
    # deleted out from under a User who had planned to map it.
    blockface = models.ForeignKey(Blockface, on_delete=models.PROTECT)
    is_mapping_with_paper = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    canceled_at = models.DateTimeField(null=True)
