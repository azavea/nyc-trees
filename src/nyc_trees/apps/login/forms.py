# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import floppyforms.__future__ as forms

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.safestring import mark_safe

from registration.forms import RegistrationFormUniqueEmail

from apps.core.models import User, Group

from django.contrib.auth.forms import AuthenticationForm
from django.template.loader import render_to_string


class NycAuthenticationForm(AuthenticationForm):
    username = forms.CharField(max_length=254,
                               label="Username or Email Address")

    error_messages = {
        'invalid_login': 'Please enter a correct username or email address '
                         'and password. Note that password is case-sensitive',
        'inactive': 'Please click the account activation link you received by '
                    'email before trying to log in.'
    }

    def confirm_login_allowed(self, user):
        # Overrides the base implementation to allow safe HTML content in the
        # validation error message
        if not user.is_active:
            msg = render_to_string(
                'login/partials/inactive_validation_message.html',
                {'text': self.error_messages['inactive']})
            raise forms.ValidationError(
                mark_safe(msg),
                code='inactive',
            )


class ForgotUsernameForm(forms.Form):
    email = forms.EmailField(label='Email address')


class SendActivationEmailForm(forms.Form):
    email = forms.EmailField(label='Email address')


class NycRegistrationForm(RegistrationFormUniqueEmail):
    tos = forms.BooleanField(
        widget=forms.CheckboxInput,
        label=mark_safe('I agree to the <a href="'
                        'http://www1.nyc.gov/home/terms-of-use.page"'
                        ' target="new">terms of use</a>'),
        error_messages={
            'required': 'You must agree to the terms to register'
        }
    )
    age_over_13 = forms.BooleanField(
        widget=forms.CheckboxInput,
        label='I am over 13 years old',
        required=False
    )

    def clean_username(self):
        username = self.cleaned_data['username']

        if username.lower() in User.reserved_usernames:
            raise ValidationError('This username is not available.')

        if User.objects.filter(email__iexact=username).exists():
            raise ValidationError('That username is already in use. '
                                  'Please supply a different username.')

        return super(NycRegistrationForm, self).clean_username()

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(username__iexact=email).exists():
            raise ValidationError('That email address is already in use. '
                                  'Please supply a different email address.')

        return super(NycRegistrationForm, self).clean_email()


class UsernameOrEmailPasswordResetForm(forms.Form):
    '''
    Django 1.8 will expose an overridable ``get_users`` method
    that separates the filtering logic from the email sending
    logic. This is not available in 1.7, so the ``save`` method in
    this form was copied from
    https://github.com/django/django/blob/59fec1ca9b3c426466f0c613a5ecf2badb992460/django/contrib/auth/forms.py#L230-L276  # NOQA
    and slighly modified.
    '''
    email_or_username = forms.CharField(label="Email or Username",
                                        max_length=254)

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        from django.core.mail import send_mail
        email_or_username = self.cleaned_data["email_or_username"]
        for user in self.get_users(email_or_username):
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            context = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            subject = loader.render_to_string(subject_template_name, context)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            email = loader.render_to_string(email_template_name, context)

            if html_email_template_name:
                html_email = loader.render_to_string(html_email_template_name,
                                                     context)
            else:
                html_email = None
            send_mail(subject, email, from_email, [user.email],
                      html_message=html_email)

    def get_users(self, email_or_username):
        matched_username_or_email_q = Q(email__iexact=email_or_username) | \
            Q(username__iexact=email_or_username)
        matched_and_active_q = Q(is_active=True) & matched_username_or_email_q

        active_users = get_user_model()._default_manager\
                                       .filter(matched_and_active_q)

        return (u for u in active_users if u.has_usable_password())


class OptionalInfoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(OptionalInfoForm, self).__init__(*args, **kwargs)
        self.fields['referrer_parks'].queryset = \
            Group.objects.filter(is_active=True)
        self.fields['referrer_parks'].widget.attrs['class'] = 'hidden'
        self.fields['referrer_group'].widget.attrs['class'] = 'hidden'
        self.fields['referrer_ad'].widget.attrs['class'] = 'hidden'
        self.fields['referrer_other'].widget.attrs['class'] = 'hidden'

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'zip_code',
                  'referrer_parks', 'referrer_group', 'referrer_ad',
                  'referrer_social_media', 'referrer_friend', 'referrer_311',
                  'referrer_other', 'opt_in_stewardship_info')
