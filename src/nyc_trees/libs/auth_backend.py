# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.auth.backends import ModelBackend

from apps.core.models import User


class EmailOrUsernameAuthentication(ModelBackend):
    def authenticate(self, username=None, password=None):
        user = None
        try:
            user = User.objects.get(email__iexact=username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username__iexact=username)
            except User.DoesNotExist:
                pass

        if user is None:
            # From the Django ModelBackend:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            User().set_password(password)
            return None

        if user.check_password(password):
            return user
        else:
            return None
