# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.timezone import now

from apps.core.models import User, Group

from libs.mixins import NycModel


class Blockface(NycModel, models.Model):
    geom = models.MultiLineStringField()
    is_available = models.BooleanField(default=True)
    expert_required = models.BooleanField(default=False)
    source = models.CharField(max_length=255, default='unknown')
    objects = models.GeoManager()

    def __unicode__(self):
        return '%s (available: %s)' % (self.pk, self.is_available)


class Territory(NycModel, models.Model):
    group = models.ForeignKey(Group)
    blockface = models.OneToOneField(Blockface)

    def __unicode__(self):
        return '%s -> %s' % (self.group, self.blockface_id)

    class Meta:
        verbose_name_plural = "Territories"


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

    def get_absolute_url(self):
        return reverse('survey_detail', args=[self.pk])


class Species(NycModel, models.Model):
    scientific_name = models.CharField(max_length=100)
    common_name = models.CharField(max_length=100)
    cultivar = models.CharField(max_length=100, blank=True)

    forms_id = models.CharField(max_length=10)
    species_code = models.CharField(max_length=10)

    def __unicode__(self):
        return '%s [%s]' % (self.common_name, self.scientific_name)

    class Meta:
        unique_together = ("scientific_name", "cultivar", "common_name")
        ordering = ['common_name', 'scientific_name', 'cultivar']
        verbose_name_plural = "Species"


CURB_CHOICES = (
    ('OnCurb', 'Along the curb'),
    ('OffsetFromCurb', 'Offset from the curb'),
)


STATUS_CHOICES = (
    ('Alive', 'Tree is alive'),
    ('Dead', 'Tree is dead'),
    ('Stump', 'Stump < 24"'),
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
    ('1or2', '1-2'),
    ('3or4', '3-4'),
    ('4orMore', '4+'),
)


GUARD_CHOICES = (
    ('None', 'Not installed'),
    ('Helpful', 'Helpful'),
    ('Harmful', 'Harmful'),
    ('Unsure', 'Unsure'),
)


SIDEWALK_CHOICES = (
    ('NoDamage', 'No damage'),
    ('Damage', 'Cracks or raised'),
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
     ('BranchLights', 'Lights or wires'),
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

    distance_to_tree = models.FloatField()
    distance_to_end = models.FloatField(null=True, blank=True)

    circumference = models.PositiveIntegerField(null=True, blank=True)
    stump_diameter = models.PositiveIntegerField(null=True, blank=True)

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

    def __unicode__(self):
        t = 'id: %s - survey: %s - dist: %s'
        return t % (self.id, self.survey.id, self.distance_to_tree)

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

        if self.distance_to_tree is not None and self.distance_to_tree < 0:
            raise ValidationError({'distance_to_tree': ['Cannot be negative']})

        if self.distance_to_end is not None and self.distance_to_end < 0:
            raise ValidationError({'distance_to_end': ['Cannot be negative']})

        if self.circumference is not None and self.circumference <= 0:
            raise ValidationError({'circumference': ['Must be positive']})

        if self.stump_diameter is not None and self.stump_diameter <= 0:
            raise ValidationError({'stump_diameter': ['Must be positive']})

        if self.status in {'Alive', 'Dead'}:
            if not self.circumference:
                raise ValidationError({'circumference': ['Field is required']})
            if self.stump_diameter:
                raise ValidationError(
                    {'stump_diameter': ['Only valid for Stumps']})
        elif self.status == 'Stump':
            if not self.stump_diameter:
                raise ValidationError(
                    {'stump_diameter': ['Field is required']})
            if self.circumference:
                raise ValidationError(
                    {'circumference': ['Not valid for Stumps']})


class ReservationsQuerySet(models.QuerySet):
    def current(self):
        return self \
            .filter(canceled_at__isnull=True) \
            .filter(expires_at__gt=now()) \
            .filter(blockface__is_available=True)

    def remaining_for(self, user):
        return self.filter(user=user).current().count()


class BlockfaceReservation(NycModel, models.Model):
    user = models.ForeignKey(User)
    # We do not plan on Blockface records being deleted, but we should
    # make sure that a Blockface that has been reserved cannot be
    # deleted out from under a User who had planned to map it.
    blockface = models.ForeignKey(Blockface, on_delete=models.PROTECT)
    is_mapping_with_paper = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    canceled_at = models.DateTimeField(null=True, blank=True)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)

    objects = ReservationsQuerySet.as_manager()

    def __unicode__(self):
        return '%s -> %s' % (self.user, self.blockface_id)
