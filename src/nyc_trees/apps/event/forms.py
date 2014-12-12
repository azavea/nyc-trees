# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from datetime import datetime

from floppyforms.__future__ import ModelForm, DateField, TimeField

from apps.event.models import Event


class EventForm(ModelForm):
    date = DateField()
    begins_at_time = TimeField()
    ends_at_time = TimeField()

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
            'contact_info'
        ]

    def clean(self):
        cleaned_data = super(EventForm, self).clean()

        if all(key in cleaned_data for key in
               {'date', 'begins_at_time', 'ends_at_time'}):
            self.instance.begins_at = datetime.combine(
                cleaned_data['date'], cleaned_data['begins_at_time'])

            self.instance.ends_at = datetime.combine(
                cleaned_data['date'], cleaned_data['ends_at_time'])

        return cleaned_data
