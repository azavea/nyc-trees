# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf import settings
from django.forms import ModelForm, inlineformset_factory, ValidationError

from apps.core.models import User, Group
from apps.event.models import EventRegistration

from libs.formatters import humanize_bytes


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

    def clean_image(self):
        image = self.cleaned_data.get('image', False)
        try:
            if image._size > settings.MAX_GROUP_IMAGE_SIZE_IN_BYTES:
                size_string = humanize_bytes(image._size)
                max_size_string = humanize_bytes(
                    settings.MAX_GROUP_IMAGE_SIZE_IN_BYTES)
                raise ValidationError('Images must be less than %s in size. '
                                      'The image you uploaded is %s' % (
                                          max_size_string, size_string))
        except AttributeError:
            # If an image was not submitted, image won't have a _size property
            pass
        return image

    def __init__(self, *args, **kwargs):
        super(GroupSettingsForm, self).__init__(*args, **kwargs)
        self.fields['allows_individual_mappers'].label =\
            "I want to allow individual mappers in my group's area"
