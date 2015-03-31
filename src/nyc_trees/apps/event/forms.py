# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from datetime import datetime
from pytz import timezone

from floppyforms.__future__ import (ModelForm, DateField, TimeField,
                                    TextInput, RadioSelect)

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
            'address': TextInput(attrs={
                'placeholder': 'Search for an address'
            }),
            'is_private': RadioSelect(choices=((True, 'Private'),
                                               (False, 'Public'))),
            'includes_training': RadioSelect(choices=((False, 'Mapping'),
                                                      (True, 'Training')))
        }

    def clean(self):
        cleaned_data = super(EventForm, self).clean()
        est_tz = timezone('US/Eastern')
        right_now = now().astimezone(est_tz)
        today = right_now.date()

        if 'date' in cleaned_data:
            cleaned_date = cleaned_data['date']

            # first check if the date was changed to be in the past and if so,
            # raise on date
            if self.instance.begins_at is not None:
                prev_date = self.instance.ends_at.astimezone(est_tz).date()
            else:
                prev_date = None

            if (((prev_date is None or cleaned_date != prev_date) and
                 cleaned_date < today)):
                self.add_error('date', 'Event must not be in the past.')

            if 'ends_at_time' in cleaned_data:
                ends_at_time = cleaned_data['ends_at_time']

                # then, check if the date is the same as today, in which case
                # time matters, and if so, raise on the time if it was changed
                # to be in the past
                if self.instance.ends_at is not None:
                    prev_ends_at_time = \
                        self.instance.ends_at.astimezone(est_tz).time()
                else:
                    prev_ends_at_time = None

                if (((prev_ends_at_time is None or
                      ends_at_time != prev_ends_at_time) and
                     cleaned_date <= today and
                     ends_at_time < right_now.time())):
                    self.add_error('ends_at_time',
                                   'Event must not end in the past.')

                if 'begins_at_time' in cleaned_data:
                    begins_at_time = cleaned_data['begins_at_time']

                    # last check, make sure the bounds are in the correct order
                    if begins_at_time > ends_at_time:
                        self.add_error('begins_at_time',
                                       'Must occur before end time.')

                    if not self.errors:
                        self.instance.begins_at = datetime.combine(
                            cleaned_data['date'],
                            cleaned_data['begins_at_time'])

                        self.instance.ends_at = datetime.combine(
                            cleaned_data['date'], cleaned_data['ends_at_time'])

        return cleaned_data
