# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.forms import ModelForm, inlineformset_factory

from apps.core.models import User, Group
from apps.event.models import EventRegistration


class ProfileSettingsForm(ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'opt_in_stewardship_info',
        ]


class PrivacySettingsForm(ModelForm):
    class Meta:
        model = User
        fields = [
            'profile_is_public',
            'real_name_is_public',
            'group_follows_are_public',
            'contributions_are_public',
            'achievements_are_public',
        ]


EventRegistrationFormSet = inlineformset_factory(
    User, EventRegistration, fields=['opt_in_emails'], extra=0)


class GroupSettingsForm(ModelForm):
    class Meta:
        model = Group
        fields = [
            'description',
            'contact_name',
            'contact_email',
            'contact_url',
            'image',
            'allows_individual_mappers'
        ]

    def __init__(self, *args, **kwargs):
        super(GroupSettingsForm, self).__init__(*args, **kwargs)
        self.fields['allows_individual_mappers'].label =\
            "I want to allow individual mappers in my group's area"
