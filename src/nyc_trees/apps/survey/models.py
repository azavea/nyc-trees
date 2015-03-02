# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from apps.core.models import User, Group

from libs.mixins import NycModel


class Blockface(NycModel, models.Model):
    geom = models.MultiLineStringField()
    is_available = models.BooleanField(default=True)
    expert_required = models.BooleanField(default=False)

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
    has_trees = models.BooleanField()
    is_mapped_in_blockface_polyline_direction = models.BooleanField()
    is_left_side = models.BooleanField()
    quit_reason = models.TextField(blank=True)

    def __unicode__(self):
        return 'block %s on %s by %s' % (self.blockface_id, self.created_at,
                                         self.user)


class Species(NycModel, models.Model):
    name = models.CharField(max_length=200, unique=True)


CURB_CHOICES = (
    ('OnCurb', 'Tree bed is along the curb'),
    ('OffsetFromCurb', 'Tree bed is offset from the curb'),
)


STATUS_CHOICES = (
    ('Alive', 'Tree is alive'),
    ('Dead', 'Tree is dead'),
    ('Stump', 'Stump [<24"]'),
)


CERTAINTY_CHOICES = (
    ('Yes', 'Yes'),
    ('No', 'No'),
    ('Maybe', 'Maybe'),
)


HEALTH_CHOICES = (
    ('Good', 'Good'),
    ('Fair', 'Fair'),
    ('Poor', 'Poor'),
)


STEWARDSHIP_CHOICES = (
    ('None', 'Zero'),
    ('1or2', 'One to two'),
    ('3or4', 'Three to four'),
    ('4orMore', 'More than four'),
)


GUARD_CHOICES = (
    ('None', 'No guard installed'),
    ('Helpful', 'Helpful guard installed'),
    ('Harmful', 'Harmful guard installed'),
    ('Unsure', 'Unsure if guard is helpful or harmful'),
)


SIDEWALK_CHOICES = (
    ('NoDamage', 'No damage is seen'),
    ('Damage', 'Cracks or raised sidewalk seen'),
)


PROBLEMS_CHOICES = (
    ('None', 'No problems'),
    ('Root problems', (
     ('Stones', 'Sidewalk or stones'),
     ('MetalGrates', 'Metal grates'),
     ('RootOther', 'Other'))),
    ('Trunk problems', (
     ('WiresRope', 'Wires or rope'),
     ('TrunkLights', 'Lights'),
     ('TrunkOther', 'Other'))),
    ('Branch problems', (
     ('BranchLights', 'Lights'),
     ('Sneakers', 'Sneakers'),
     ('BranchOther', 'Other')))
)


def flatten_categorized_choices(choices):
    flat = []
    for choice in choices:
        if isinstance(choice[1], tuple):
            for group_choice in choice[1:]:
                flat.extend(group_choice)
        else:
            flat.append(choice)
    return tuple(flat)


class Tree(NycModel, models.Model):
    survey = models.ForeignKey(Survey)
    # We do not anticipate deleting a Species, but we definitely
    # should not allow it to be deleted if there is a related Tree
    species = models.ForeignKey(Species, null=True, blank=True,
                                on_delete=models.PROTECT)
    # TODO: Parks may want floats
    distance_to_tree = models.PositiveIntegerField()
    distance_to_end = models.PositiveIntegerField(null=True, blank=True)
    # TODO: Parks may want to separate circumferences/diameter fields.
    # If so, switch to PositiveIntegerField and add clean() test that
    # diameter is specified only for stumps.
    # If not, add clean() test that circumference > 0
    circumference = models.FloatField()
    curb_location = models.CharField(max_length=25, choices=CURB_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES)

    # The following fields are collected only when status == 'Alive',
    # hence blank=True

    species_certainty = models.CharField(
        blank=True, max_length=15, choices=CERTAINTY_CHOICES)
    health = models.CharField(
        blank=True, max_length=15, choices=HEALTH_CHOICES)
    stewardship = models.CharField(
        blank=True, max_length=15, choices=STEWARDSHIP_CHOICES)
    guards = models.CharField(
        blank=True, max_length=15, choices=GUARD_CHOICES)
    sidewalk_damage = models.CharField(
        blank=True, max_length=15, choices=SIDEWALK_CHOICES)
    problems = models.CharField(blank=True, max_length=130)

    def clean(self):
        if self.status != 'Alive':
            self.species_certainty = ''
            self.health = ''
            self.stewardship = ''
            self.guards = ''
            self.sidewalk_damage = ''
            self.problems = ''

        if self.problems:
            probs = self.problems.split(',')
            if len(probs) != len(set(probs)):
                raise ValidationError({'problems': ['Duplicate entry']})
            codes = [pair[0]
                     for pair in flatten_categorized_choices(PROBLEMS_CHOICES)]
            for code in probs:
                if code not in codes:
                    raise ValidationError({'problems': [
                        'Invalid entry: %s' % code]})


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
