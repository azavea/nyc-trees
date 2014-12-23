# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.forms import Form, BooleanField, CheckboxInput, EmailField

from registration.forms import RegistrationFormUniqueEmail


class ForgotUsernameForm(Form):
    email = EmailField(label='Your email address')


class NycRegistrationForm(RegistrationFormUniqueEmail):
    tos = BooleanField(
        widget=CheckboxInput,
        label='I agree to the terms of use',
        error_messages={
            'required': 'You must agree to the terms to register'
        }
    )
    age_over_13 = BooleanField(
        widget=CheckboxInput,
        label='I am over 13 years old',
        required=False
    )
