# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import django.contrib.auth.views as contrib_auth

from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.shortcuts import redirect

from apps.core.models import User
from apps.login.forms import (ForgotUsernameForm,
                              UsernameOrEmailPasswordResetForm,
                              OptionalInfoForm)


def logout(request):
    return contrib_auth.logout(request, next_page=reverse('home_page'))


def password_reset(request):
    return contrib_auth.password_reset(
        request,
        password_reset_form=UsernameOrEmailPasswordResetForm)


def forgot_username_page(request):
    if request.method == 'GET':
        form = ForgotUsernameForm()
    else:
        form = ForgotUsernameForm(request.POST)
    return {'form': form}


def forgot_username(request):
    form = ForgotUsernameForm(request.POST)
    if not form.is_valid():
        return forgot_username_page(request)

    email = form.cleaned_data['email']
    users = User.objects.filter(email=email)

    # Don't reveal if we don't have that email, to prevent email harvesting
    if len(users) == 1:
        user = users[0]

        password_reset_url = request.build_absolute_uri(
            reverse('auth_password_reset'))

        subject = 'Account Recovery'
        body = render_to_string('login/forgot_username_email.txt',
                                {'user': user,
                                 'password_url': password_reset_url})

        user.email_user(subject, body, settings.DEFAULT_FROM_EMAIL)

    return redirect('forgot_username_sent')


def forgot_username_sent(request):
    return {}


def activation_complete(request):
    form = OptionalInfoForm(instance=request.user)
    return {
        'form': form
    }


def save_optional_info(request):
    form = OptionalInfoForm(request.POST, instance=request.user)
    # This shouldn't happen since all fields on this form are optional.
    if not form.is_valid():
        return {
            'form': form
        }
    form.save()
    return redirect('home_page')
