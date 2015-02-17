# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.gis.db import models
from django.utils.timezone import now

from apps.core.models import User, Group

from libs.mixins import NycModel


class Blockface(NycModel, models.Model):
    geom = models.MultiLineStringField()
    is_available = models.BooleanField(default=True)

    objects = models.GeoManager()

    def __unicode__(self):
        return '%s (available: %s)' % (self.pk, self.is_available)


class Territory(NycModel, models.Model):
    group = models.ForeignKey(Group)
    blockface = models.OneToOneField(Blockface)

    def __unicode__(self):
        return '%s -> %s' % (self.group, self.blockface_id)


class Survey(NycModel, models.Model):
    # We do not anticipate deleting a Blockface, but we definitely
    # should not allow it to be deleted if there is a related Survey
    blockface = models.ForeignKey(Blockface, on_delete=models.PROTECT)
    # We do not want to lose survey data by allowing the deletion of
    # a User object to automatically cascade and delete the Survey
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    teammate = models.ForeignKey(User, null=True, on_delete=models.PROTECT,
                                 related_name='surveys_as_teammate',
                                 blank=True)
    is_flagged = models.BooleanField(default=False)

    def __unicode__(self):
        return 'block %s on %s by %s' % (self.blockface_id, self.created_at,
                                         self.user)


class Species(NycModel, models.Model):
    name = models.CharField(max_length=200, unique=True)


class Tree(NycModel, models.Model):
    survey = models.ForeignKey(Survey)
    # We do not anticipate deleting a Species, but we definitely
    # should not allow it to be deleted if there is a related Tree
    species = models.ForeignKey(Species, null=True, on_delete=models.PROTECT)


class ReservationsQuerySet(models.QuerySet):
    def current(self):
        return self \
            .filter(canceled_at__isnull=True) \
            .filter(expires_at__gt=now())


class BlockfaceReservation(NycModel, models.Model):
    user = models.ForeignKey(User)
    # We do not plan on Blockface records being deleted, but we should
    # make sure that a Blockface that has been reserved cannot be
    # deleted out from under a User who had planned to map it.
    blockface = models.ForeignKey(Blockface, on_delete=models.PROTECT)
    is_mapping_with_paper = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    canceled_at = models.DateTimeField(null=True, blank=True)

    objects = ReservationsQuerySet.as_manager()

    def __unicode__(self):
        return '%s -> %s' % (self.user, self.blockface_id)
