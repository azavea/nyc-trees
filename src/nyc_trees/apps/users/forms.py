# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.forms import ModelForm

from apps.core.models import User


class ProfileSettingsForm(ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'opt_in_events_info',
            'opt_in_stewardship_info',
            'profile_is_public',
            'real_name_is_public',
            'group_follows_are_public',
            'contributions_are_public',
            'achievements_are_public',
        ]
