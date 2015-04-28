# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.text import slugify

from libs.mixins import NycModel
from libs.pdf_maps import url_if_cooked


REFERRER_PARKS = (
    ('website', 'Website'),
    ('newsletter', 'Newsletter'),
    ('employee', 'I am a Parks employee')
)

REFERRER_AD = (
    ('bus', 'Bus Poster'),
    ('subway', 'Subway Poster'),
    ('tv', 'Television'),
    ('radio', 'Radio'),
    ('website', 'Website')
)


class NycUserManager(UserManager):
    def get_by_natural_key(self, username):
        # For login, make username case-insensitive
        return self.get(username__iexact=username)


#######################################
# When adding new fields to the User model, please take care to add these
# fields to the NycUserAdmin class as well, so that we may administer these
# fields in the Django super admin.
# Ref: src/nyc_trees/apps/core/admin.py
#######################################
class User(NycModel, AbstractUser):
    individual_mapper = models.NullBooleanField()
    requested_individual_mapping_at = models.DateTimeField(null=True,
                                                           blank=True)

    profile_is_public = models.BooleanField(default=False)
    real_name_is_public = models.BooleanField(default=False)
    group_follows_are_public = models.BooleanField(default=False)
    contributions_are_public = models.BooleanField(default=False)
    achievements_are_public = models.BooleanField(default=False)

    is_flagged = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    is_ambassador = models.BooleanField(default=False)
    is_minor = models.BooleanField(default=False)

    zip_code = models.CharField(max_length=25, default='', blank=True)

    referrer_parks = models.CharField(max_length=25, default='', blank=True,
                                      choices=REFERRER_PARKS)
    referrer_group = models.ForeignKey('Group', on_delete=models.PROTECT,
                                       null=True, blank=True)
    referrer_ad = models.CharField(max_length=25, default='', blank=True,
                                   choices=REFERRER_AD)
    referrer_social_media = models.BooleanField(default=False)
    referrer_friend = models.BooleanField(default=False)
    referrer_311 = models.BooleanField(default=False)
    referrer_other = models.CharField(max_length=255, default='', blank=True)

    field_training_complete = models.BooleanField(default=False)
    training_finished_getting_started = models.BooleanField(default=False)
    training_finished_the_mapping_method = models.BooleanField(default=False)
    training_finished_tree_data = models.BooleanField(default=False)
    training_finished_tree_surroundings = models.BooleanField(default=False)
    training_finished_wrapping_up = models.BooleanField(default=False)
    training_finished_intro_quiz = models.BooleanField(default=False)
    training_finished_groups_to_follow = models.BooleanField(default=False)

    opt_in_stewardship_info = models.BooleanField(default=False)

    progress_page_help_shown = models.BooleanField(default=False)
    reservations_page_help_shown = models.BooleanField(default=False)

    reservation_ids_in_map_pdf = models.TextField(default='', blank=True)
    reservations_map_pdf_filename = models.CharField(
        max_length=255, default='', blank=True)

    objects = NycUserManager()

    privacy_fields = {'profile_is_public': 'profile',
                      'real_name_is_public': 'real name',
                      'group_follows_are_public': 'group follows',
                      'contributions_are_public': 'contributions',
                      'achievements_are_public': 'achievements'}

    # Please keep in sync with special `/user/*` endpoints.
    # Ref: src/nyc_trees/apps/users/urls/user.py
    reserved_usernames = ('profile',
                          'settings',
                          'achievements')

    def clean(self):
        if ((User.objects.exclude(pk=self.pk)
             .filter(email__iexact=self.email).exists())):
            raise ValidationError({'email': [
                'This email address is already in use. '
                'Please supply a different email address.']
            })

        if self.is_minor:
            for field, name in User.privacy_fields.iteritems():
                if getattr(self, field, False):
                    raise ValidationError({field: [
                        'A tree mapper under 13 years of age cannot make '
                        'their %s public.' % name]})

        self.first_name = self.first_name.strip()
        self.last_name = self.last_name.strip()

    def get_absolute_url(self):
        return reverse('user_detail', args=[self.username])

    @property
    def online_training_complete(self):
        from apps.home.training import training_summary
        return training_summary.is_complete(self)

    @property
    def training_complete(self):
        return self.online_training_complete and self.field_training_complete

    def attended_at_least_two_events(self):
        from apps.event.models import EventRegistration
        return EventRegistration.objects.filter(user=self,
                                                did_attend=True).count() >= 2

    def eligible_to_become_individual_mapper(self):
        """
        Return True if user has completed online training, attended a mapping
        event, and one other training/mapping event.
        Return False if user is *already* an individual mapper or their mapper
        status was rescinded.
        """
        if self.individual_mapper is None:
            return (self.field_training_complete and
                    self.attended_at_least_two_events())
        return False

    def eligible_to_become_trusted_mapper(self, group):
        from apps.core.helpers import (user_is_group_admin,
                                       user_is_trusted_mapper)
        return self.individual_mapper is True and \
            group.allows_individual_mappers and \
            not user_is_group_admin(self, group) and \
            not user_is_trusted_mapper(self, group)

    @property
    def surveys(self):
        """Return surveys user has participated in"""
        from apps.survey.models import Survey
        return Survey.objects.filter(Q(user=self) | Q(teammate=self))

    @property
    def blocks_mapped_count(self):
        return self.surveys.distinct('blockface').count()

    @property
    def reservations_map_pdf_url(self):
        return url_if_cooked(self.reservations_map_pdf_filename)

    class Meta:
        ordering = ['username']


def _generate_image_filename(group, filename):
    return 'group_images/{}/{}'.format(group.slug, filename)


class Group(NycModel, models.Model):
    name = models.CharField(max_length=255, unique=True)
    # blank=True is valid for 'slug', because we'll automatically create slugs
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(default='', blank=True)
    contact_name = models.CharField(max_length=255, default='', blank=True)
    contact_email = models.EmailField(null=True)
    contact_url = models.URLField(null=True, blank=True)
    # Deleting a user should not cascade delete the group of which
    # they are an admin. A new admin should be set before a user
    # delete is allowed.
    admin = models.ForeignKey(User, null=True, blank=True,
                              on_delete=models.PROTECT)
    image = models.ImageField(null=True, blank=True,
                              upload_to=_generate_image_filename)
    is_active = models.BooleanField(default=True)
    allows_individual_mappers = models.BooleanField(default=False)
    affiliation = models.CharField(max_length=255, default='', blank=True)
    border = models.MultiPolygonField(null=True, blank=True)
    # Territory is one of the few models used in our tiler queries for which we
    # expect deletions to regularly occur.  Since the 'updated_at' field won't
    # change on any Territory rows, we record territory changes on the Group
    # and check the group when trying to find out the Territory cache buster
    territory_updated_at = models.DateTimeField(null=True, blank=True,
                                                db_index=True)

    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

    def clean(self):
        if not self.slug:
            self.slug = slugify(self.name)

    def get_absolute_url(self):
        return reverse('group_detail', kwargs={'group_slug': self.slug})

    class Meta:
        ordering = ['name']


class TaskRun(models.Model):
    name = models.CharField(max_length=255)
    date_started = models.DateField()
    task_result_id = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        unique_together = ("name", "date_started")
