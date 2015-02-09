# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from datetime import datetime

from floppyforms.__future__ import ModelForm, DateField, TimeField, RadioSelect

from django.utils.timezone import now

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
        right_now = now()
        today = right_now.date()

        if 'date' in cleaned_data:
            cleaned_date = cleaned_data['date']

            # first check if the date is in the past and if so, raise on date
            if cleaned_date < today:
                Event.raise_date_past('date')
            if 'begins_at_time' in cleaned_data:
                begins_at_time = cleaned_data['begins_at_time']

                # then, check if the date is the same as today, in which case
                # time matters, and if so, raise on the time
                if cleaned_date == today and begins_at_time < right_now.time():
                    Event.raise_date_past('begins_at_time')

                if 'ends_at_time' in cleaned_data:
                    ends_at_time = cleaned_data['ends_at_time']

                    # last check, make sure the bounds are in the correct order
                    if begins_at_time > ends_at_time:
                        Event.raise_invalid_bounds('begins_at_time')
                    self.instance.begins_at = datetime.combine(
                        cleaned_data['date'], cleaned_data['begins_at_time'])

                    self.instance.ends_at = datetime.combine(
                        cleaned_data['date'], cleaned_data['ends_at_time'])

        return cleaned_data
