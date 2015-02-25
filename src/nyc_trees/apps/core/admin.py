# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.core.exceptions import ValidationError

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from apps.core.models import User, Group


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class NycUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class NycUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    # Django auth has hard-coded references to the default `User` model so
    # we have to reimplement this function with the correct references.
    # Source: http://stackoverflow.com/questions/16953302/django-custom-user-model-in-admin-relation-auth-user-does-not-exist  # NOQA
    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise ValidationError(self.error_messages['duplicate_username'])


@admin.register(User)
class NycUserAdmin(UserAdmin):
    form = NycUserChangeForm
    add_form = NycUserCreationForm

    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('zip_code',
                                      'opt_in_stewardship_info',
                                      'individual_mapper',
                                      'requested_individual_mapping_at')}),

        ('Permissions', {'fields': ('profile_is_public',
                                    'real_name_is_public',
                                    'group_follows_are_public',
                                    'contributions_are_public',
                                    'achievements_are_public',
                                    'is_flagged',
                                    'is_banned',
                                    'is_census_admin',
                                    'is_ambassador',
                                    'is_minor')}),

        ('Referrer', {'fields': ('referrer_parks',
                                 'referrer_group',
                                 'referrer_ad',
                                 'referrer_social_media',
                                 'referrer_friend',
                                 'referrer_311',
                                 'referrer_other')}),

        ('Training', {'fields': ('field_training_complete',
                                 'training_finished_getting_started',
                                 'training_finished_the_mapping_method',
                                 'training_finished_tree_data',
                                 'training_finished_tree_surroundings',
                                 'training_finished_intro_quiz',
                                 'training_finished_groups_to_follow')})
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('email',)}),
    )
