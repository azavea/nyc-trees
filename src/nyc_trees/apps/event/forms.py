# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from datetime import datetime

from floppyforms.__future__ import ModelForm, DateField, TimeField, RadioSelect

from django.core.exceptions import ValidationError

from apps.event.models import Event


TIMEFIELD_FORMATS = (
    '%H:%M',
    '%H:%M:%S',
    '%I:%M %p'
)


class EventForm(ModelForm):
    date = DateField()
    begins_at_time = TimeField(input_formats=TIMEFIELD_FORMATS)
    ends_at_time = TimeField(input_formats=TIMEFIELD_FORMATS)

    class Meta:
        model = Event
        fields = [
            'group',
            'title',
            'address',
            'location',
            'location_description',
            'description',
            'is_private',
            'includes_training',
            'max_attendees',
            'contact_email',
            'contact_name'
        ]
        widgets = {
            'is_private': RadioSelect(choices=((True, 'Private'),
                                               (False, 'Public'))),
            'includes_training': RadioSelect(choices=((False, 'Mapping'),
                                                      (True, 'Training')))
        }

    def clean(self):
        cleaned_data = super(EventForm, self).clean()

        if 'begins_at_time' in cleaned_data and 'ends_at_time' in cleaned_data:
            if cleaned_data['begins_at_time'] > cleaned_data['ends_at_time']:
                raise ValidationError({
                    'begins_at_time': ['Start time must be before end time']
                })
            if 'date' in cleaned_data:
                self.instance.begins_at = datetime.combine(
                    cleaned_data['date'], cleaned_data['begins_at_time'])

                self.instance.ends_at = datetime.combine(
                    cleaned_data['date'], cleaned_data['ends_at_time'])

        return cleaned_data
