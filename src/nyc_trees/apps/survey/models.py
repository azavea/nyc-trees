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


class Borough(NycModel, models.Model):
    geom = models.MultiPolygonField()
    name = models.CharField(max_length=32)
    code = models.IntegerField(db_index=True, unique=True)


class NeighborhoodTabulationArea(NycModel, models.Model):
    geom = models.MultiPolygonField()
    name = models.CharField(max_length=75)
    code = models.CharField(max_length=4, db_index=True, unique=True)


class Blockface(models.Model):
    geom = models.MultiLineStringField(
        help_text='Coordinates of blockface polyline')
    is_available = models.BooleanField(
        default=True,
        help_text='Is blockface available for surveying?')
    expert_required = models.BooleanField(
        default=False,
        help_text='Is an expert required to survey this blockface?')
    source = models.CharField(
        max_length=255, default='unknown',
        help_text='Source for blockface data (borough name)')
    borough = models.ForeignKey(
        Borough, null=True,
        help_text='The borough containing this blockface')
    nta = models.ForeignKey(
        NeighborhoodTabulationArea, null=True,
        help_text='The neighborhood tabulation area containing this blockface')

    # We can't use the NycModel mixin, because we want to add db indexes
    created_at = models.DateTimeField(
        auto_now_add=True, editable=False,
        help_text='Time when row was created')
    updated_at = models.DateTimeField(
        auto_now=True, db_index=True, editable=False,
        help_text='Time when row was last updated'
    )

    objects = models.GeoManager()

    def __unicode__(self):
        return '%s (available: %s)' % (self.pk, self.is_available)


class Territory(NycModel, models.Model):
    group = models.ForeignKey(
        Group,
        help_text='ID of group responsible for surveying blockface')
    blockface = models.OneToOneField(
        Blockface,
        help_text='ID of blockface')

    def __unicode__(self):
        return '%s -> %s' % (self.group, self.blockface_id)

    class Meta:
        verbose_name_plural = "Territories"


class SurveyQuerySet(models.QuerySet):
    def complete(self):
        return self.filter(quit_reason='')


class Survey(models.Model):
    # We do not anticipate deleting a Blockface, but we definitely
    # should not allow it to be deleted if there is a related Survey
    blockface = models.ForeignKey(
        Blockface, on_delete=models.PROTECT,
        help_text='ID of blockface surveyed')
    # We do not want to lose survey data by allowing the deletion of
    # a User object to automatically cascade and delete the Survey
    user = models.ForeignKey(
        User, on_delete=models.PROTECT,
        help_text='ID of user performing survey')
    teammate = models.ForeignKey(
        User, null=True, on_delete=models.PROTECT,
        related_name='surveys_as_teammate',
        blank=True,
        help_text='ID of user helping with survey')
    is_flagged = models.BooleanField(
        default=False,
        help_text='Did user request a review for this survey?')
    has_trees = models.BooleanField(
        help_text='Did blockface contain any trees?')
    is_mapped_in_blockface_polyline_direction = models.BooleanField(
        help_text='Does survey begin at first point of blockface polyline?')
    is_left_side = models.BooleanField(
        help_text='Was left side of block surveyed?')
    quit_reason = models.TextField(
        blank=True,
        help_text='Description of why survey was abandoned')

    # We can't use the NycModel mixin, because we want to add db indexes
    created_at = models.DateTimeField(
        auto_now_add=True, editable=False,
        help_text='Time when row was created')
    updated_at = models.DateTimeField(
        auto_now=True, db_index=True, editable=False,
        help_text='Time when row was last updated'
    )

    objects = SurveyQuerySet.as_manager()

    def __unicode__(self):
        return 'block %s on %s by %s' % (self.blockface_id, self.created_at,
                                         self.user)

    def get_absolute_url(self):
        return reverse('survey_detail', args=[self.pk])


class Species(NycModel, models.Model):
    scientific_name = models.CharField(
        max_length=100,
        help_text='Scientific name for species, e.g. "Acer Rubrum"')
    common_name = models.CharField(
        max_length=100,
        help_text='Common name for species, e.g. "Red Maple"')
    cultivar = models.CharField(
        max_length=100, blank=True,
        help_text='Further qualifies scientific name')

    forms_id = models.CharField(
        max_length=10,
        help_text='ID from original data source')
    species_code = models.CharField(
        max_length=10,
        help_text='Species code from original data source')

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
    ('Stump', 'Stump (<24" tall)'),
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
    survey = models.ForeignKey(
        Survey,
        help_text='ID of survey containing this tree')
    # We do not anticipate deleting a Species, but we definitely
    # should not allow it to be deleted if there is a related Tree
    species = models.ForeignKey(
        Species, null=True, blank=True, on_delete=models.PROTECT,
        help_text='ID of tree species')
    distance_to_tree = models.FloatField(
        help_text='Measured distance to tree (feet)')
    distance_to_end = models.FloatField(
        null=True, blank=True,
        help_text='Measured distance to end of block (feet) '
                  '[only if final tree in survey]')

    circumference = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Measured circumference (inches) [if not a stump]')
    stump_diameter = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Measured diameter (inches) [if a stump]')

    curb_location = models.CharField(
        max_length=25, choices=CURB_CHOICES,
        help_text='Location of tree bed')
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES,
        help_text='Is this tree alive, dead, or a stump?')

    # The following fields are collected only when status == 'Alive',
    # hence blank=True

    species_certainty = models.CharField(
        blank=True, max_length=15, choices=CERTAINTY_CHOICES,
        help_text='How certain is user of species? [if alive]')
    health = models.CharField(
        blank=True, max_length=15, choices=HEALTH_CHOICES,
        help_text='Perception of tree health [if alive]')
    stewardship = models.CharField(
        blank=True, max_length=15, choices=STEWARDSHIP_CHOICES,
        help_text='Number of observed stewardship practices [if alive]')
    guards = models.CharField(
        blank=True, max_length=15, choices=GUARD_CHOICES,
        help_text='Status of tree guards [if alive]')
    sidewalk_damage = models.CharField(
        blank=True, max_length=15, choices=SIDEWALK_CHOICES,
        help_text='Observed sidewalk damage [if alive]')
    problems = models.CharField(
        blank=True, max_length=130,
        help_text='Observed problems (comma-separated strings) [if alive]')

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


class BlockfaceReservation(models.Model):
    user = models.ForeignKey(
        User,
        help_text='ID of user reserving blockface')
    # We do not plan on Blockface records being deleted, but we should
    # make sure that a Blockface that has been reserved cannot be
    # deleted out from under a User who had planned to map it.
    blockface = models.ForeignKey(
        Blockface, on_delete=models.PROTECT,
        help_text='ID of blockface reserved')
    is_mapping_with_paper = models.BooleanField(
        default=False,
        help_text='Does user plan to survey using the paper form?')
    expires_at = models.DateTimeField(
        help_text='Expiration time for this reservation')
    canceled_at = models.DateTimeField(
        null=True, blank=True,
        help_text='Cancellation time [if reservation was canceled]')
    reminder_sent_at = models.DateTimeField(
        null=True, blank=True,
        help_text='Time expiration reminder was emailed')

    # We can't use the NycModel mixin, because we want to add db indexes
    created_at = models.DateTimeField(
        auto_now_add=True, editable=False,
        help_text='Time when row was created')
    updated_at = models.DateTimeField(
        auto_now=True, db_index=True, editable=False,
        help_text='Time when row was last updated'
    )

    objects = ReservationsQuerySet.as_manager()

    def __unicode__(self):
        return '%s -> %s' % (self.user, self.blockface_id)
