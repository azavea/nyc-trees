# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from datetime import timedelta

import django.contrib.auth.views as contrib_auth

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.shortcuts import redirect

from registration.models import RegistrationProfile

from django_statsd.clients import statsd

from apps.core.models import User
from apps.login.forms import (ForgotUsernameForm,
                              UsernameOrEmailPasswordResetForm,
                              OptionalInfoForm,
                              SendActivationEmailForm)


def logout(request):
    return contrib_auth.logout(request, next_page=reverse('home_page'))


def password_reset(request):
    if request.method == "POST":
        form = UsernameOrEmailPasswordResetForm(request.POST)
        if form.is_valid():
            email_or_username = form.cleaned_data["email_or_username"]
            users = User.objects \
                .filter(is_active=False) \
                .filter(Q(email__iexact=email_or_username) |
                        Q(username__iexact=email_or_username))

            if len(users) == 1:
                user = users[0]
                expiration_date = user.date_joined + timedelta(
                    settings.ACCOUNT_ACTIVATION_DAYS)
                if expiration_date > now():
                    return redirect('password_reset_resend_activation')
                else:
                    return redirect('password_reset_impossible')

    return contrib_auth.password_reset(
        request,
        password_reset_form=UsernameOrEmailPasswordResetForm,
        post_reset_redirect=reverse('password_reset_done'))


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


def send_activation_email_page(request):
    if request.method == 'GET':
        form = SendActivationEmailForm()
    else:
        form = SendActivationEmailForm(request.POST)
    return {'form': form}


def send_activation_email(request):
    form = SendActivationEmailForm(request.POST)
    if not form.is_valid():
        return send_activation_email_page(request)

    email = form.cleaned_data['email']
    users = User.objects.filter(email=email)

    # Don't reveal if we don't have that email, to prevent email harvesting
    if len(users) == 1:
        user = users[0]
        if user.is_active:
            return redirect('activated')

        site = Site.objects.get_current()

        try:
            registration_profile = RegistrationProfile.objects.get(user=user)
            registration_profile.send_activation_email(site)
            statsd.incr('email.message.types.resend_activation')
        except RegistrationProfile.DoesNotExist:
            # TODO: Generate a Registration Profile and send the email.
            # This is not likely to happen, because any user created through
            # Django registration should have a profile
            pass

    return redirect('activation_email_sent')


def activation_email_sent(request):
    return {}


def activated(request):
    return {}
