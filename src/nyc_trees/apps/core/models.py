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
    individual_mapper = models.NullBooleanField(
        help_text='Can user reserve and map block edges outside of events?')
    requested_individual_mapping_at = models.DateTimeField(
        null=True, blank=True,
        help_text='Time when user requested individual mapper status')

    profile_is_public = models.BooleanField(
        default=False,
        help_text="Can other users see this user's profile?")
    real_name_is_public = models.BooleanField(
        default=False,
        help_text="Can other users see this user's real name?")
    group_follows_are_public = models.BooleanField(
        default=False,
        help_text="Can other users see which groups this user is following?")
    contributions_are_public = models.BooleanField(
        default=False,
        help_text="Can other users see this user's mapping statistics?")
    achievements_are_public = models.BooleanField(
        default=False,
        help_text="Can other users see this user's achievements?")

    is_flagged = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    is_ambassador = models.BooleanField(default=False)
    is_minor = models.BooleanField(
        default=False,
        help_text='Is user 13 years old or under?')

    zip_code = models.CharField(
        max_length=25, default='', blank=True,
        help_text="User's ZIP Code")

    referrer_parks = models.CharField(
        max_length=25, default='', blank=True, choices=REFERRER_PARKS,
        help_text='How user learned of site (Parks sources)')
    referrer_group = models.ForeignKey(
        'Group', on_delete=models.PROTECT, null=True, blank=True,
        help_text='How user learned of site (census group sources)')
    referrer_ad = models.CharField(
        max_length=25, default='', blank=True, choices=REFERRER_AD,
        help_text='How user learned of site (ad sources)')
    referrer_social_media = models.BooleanField(
        default=False,
        help_text='Did user learn of site via social media?')
    referrer_friend = models.BooleanField(
        default=False,
        help_text='Did user learn of site via a friend?')
    referrer_311 = models.BooleanField(
        default=False,
        help_text='Did user learn of site via 311?')
    referrer_other = models.CharField(
        max_length=255, default='', blank=True,
        help_text='How user learned of site (other sources)')

    field_training_complete = models.BooleanField(
        default=False,
        help_text='Was user checked in to a mapping event?')
    training_finished_getting_started = models.BooleanField(
        default=False,
        help_text='"Getting Started" training section completed?')
    training_finished_the_mapping_method = models.BooleanField(
        default=False,
        help_text='"Mapping Method" training section completed?')
    training_finished_tree_data = models.BooleanField(
        default=False,
        help_text='"Tree Data" training section completed?')
    training_finished_tree_surroundings = models.BooleanField(
        default=False,
        help_text='"Tree Surroundings" training section completed?')
    training_finished_wrapping_up = models.BooleanField(
        default=False,
        help_text='"Wrapping Up" training section completed?')
    training_finished_intro_quiz = models.BooleanField(
        default=False,
        help_text='Intro Quiz completed?')
    training_finished_groups_to_follow = models.BooleanField(
        default=False,
        help_text='Seen invitation to follow groups?')

    opt_in_stewardship_info = models.BooleanField(
        default=False,
        help_text='User chose to receive information from Parks')

    progress_page_help_shown = models.BooleanField(
        default=False,
        help_text='Seen help text on Progress page?')
    survey_geolocate_help_shown = models.BooleanField(
        default=False,
        help_text='Seen geolocation help text on Survey page?')
    reservations_page_help_shown = models.BooleanField(
        default=False,
        help_text='Seen help text on Reservations page?')

    reservation_ids_in_map_pdf = models.TextField(
        default='', blank=True,
        help_text='IDs of reservations in PDF map')
    reservations_map_pdf_filename = models.CharField(
        max_length=255, default='', blank=True,
        help_text='S3 file path of reservations map PDF')

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
        return Survey.objects.complete().filter(
            Q(user=self) | Q(teammate=self))

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
    name = models.CharField(
        max_length=255, unique=True,
        help_text='Name of group, for display')
    # blank=True is valid for 'slug', because we'll automatically create slugs
    slug = models.SlugField(
        unique=True, blank=True, max_length=255,
        help_text='Short name for group, used in URLs')
    description = models.TextField(
        default='', blank=True,
        help_text='Description of group, for display')
    contact_name = models.CharField(
        max_length=255, default='', blank=True,
        help_text='Name of contact person for group')
    contact_email = models.EmailField(
        null=True,
        help_text='Email address of contact person for group')
    contact_url = models.URLField(
        null=True, blank=True,
        help_text="URL of group's external website")
    # Deleting a user should not cascade delete the group of which
    # they are an admin. A new admin should be set before a user
    # delete is allowed.
    admin = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.PROTECT,
        help_text='ID of user who is the group administrator')
    image = models.ImageField(
        null=True, blank=True, upload_to=_generate_image_filename,
        help_text='S3 path of uploaded group logo')
    is_active = models.BooleanField(
        default=True,
        help_text='Should this group be listed on the "Groups" page?')
    allows_individual_mappers = models.BooleanField(
        default=False,
        help_text="Can users request permission to map in group's territory?")
    affiliation = models.CharField(
        max_length=255, default='', blank=True,
        help_text='Name of organization affiliated with group')
    border = models.MultiPolygonField(
        null=True, blank=True,
        help_text='Map area associated with group')
    # Territory is one of the few models used in our tiler queries for which we
    # expect deletions to regularly occur.  Since the 'updated_at' field won't
    # change on any Territory rows, we record territory changes on the Group
    # and check the group when trying to find out the Territory cache buster
    territory_updated_at = models.DateTimeField(
        null=True, blank=True, db_index=True, editable=False,
        help_text="Time when group's block edge assignments were last updated")

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
