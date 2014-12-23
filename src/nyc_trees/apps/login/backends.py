# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from registration.backends.default.views import RegistrationView

from apps.login.forms import NycRegistrationForm


class NycRegistrationView(RegistrationView):
    def register(self, request, **cleaned_data):
        new_user = super(NycRegistrationView, self)\
            .register(request, **cleaned_data)

        new_user.is_minor = not cleaned_data['age_over_13']
        new_user.save()

        return new_user

    def get_form_class(self, request):
        return NycRegistrationForm
