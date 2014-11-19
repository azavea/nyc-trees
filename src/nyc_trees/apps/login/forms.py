# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django import forms


class ForgotUsernameForm(forms.Form):
    email = forms.EmailField(label='Your email address')
