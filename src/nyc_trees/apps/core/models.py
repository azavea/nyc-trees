# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.text import slugify

from libs.mixins import NycModel


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


class User(NycModel, AbstractUser):
    individual_mapper = models.BooleanField(default=False)
    requested_individual_mapping_at = models.DateTimeField(null=True,
                                                           blank=True)

    profile_is_public = models.BooleanField(default=False)
    real_name_is_public = models.BooleanField(default=False)
    group_follows_are_public = models.BooleanField(default=False)
    contributions_are_public = models.BooleanField(default=False)
    achievements_are_public = models.BooleanField(default=False)

    is_flagged = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    is_census_admin = models.BooleanField(default=False)
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

    training_finished_getting_started = models.BooleanField(default=False)
    training_finished_the_mapping_method = models.BooleanField(default=False)
    training_finished_tree_data = models.BooleanField(default=False)
    training_finished_tree_surroundings = models.BooleanField(default=False)
    training_finished_groups_to_follow = models.BooleanField(default=False)

    opt_in_stewardship_info = models.BooleanField(default=False)

    objects = UserManager()

    privacy_fields = {'profile_is_public': 'profile',
                      'real_name_is_public': 'real name',
                      'group_follows_are_public': 'group follows',
                      'contributions_are_public': 'contributions',
                      'achievements_are_public': 'achievements'}

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


class Group(NycModel, models.Model):
    name = models.CharField(max_length=255, unique=True)
    # blank=True is valid for 'slug', because we'll automatically create slugs
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(default='', blank=True)
    contact_name = models.CharField(max_length=255, default='', blank=True)
    contact_email = models.EmailField(null=True)
    contact_url = models.URLField(null=True)
    # Deleting a user should not cascade delete the group of which
    # they are an admin. A new admin should be set before a user
    # delete is allowed.
    admin = models.ForeignKey(User, on_delete=models.PROTECT)
    image = models.ImageField(null=True)
    is_active = models.BooleanField(default=True)
    allows_individual_mappers = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def clean(self):
        if not self.slug:
            self.slug = slugify(self.name)

    def get_absolute_url(self):
        return reverse('group_detail', kwargs={'group_slug': self.slug})
