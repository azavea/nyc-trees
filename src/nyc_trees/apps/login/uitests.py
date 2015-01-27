# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import re

from django.core import mail
from django.core.urlresolvers import reverse

from libs.ui_test_helpers import NycTreesSeleniumTestCase

from apps.core.models import User


class NycUITest(NycTreesSeleniumTestCase):
    def _get_link_from_email(self, email):
        matches = re.findall(r"http://.*$", email.body, re.MULTILINE)
        self.assertEqual(1, len(matches))
        return matches[0]


class FullRegistrationUITest(NycUITest):
    def setUp(self):
        super(FullRegistrationUITest, self).setUp()

        self.username = 'Fry'
        self.email = 'fry@planetexpress.com'
        self.password = 'password'

    def _get_or_create_user(self):
        if User.objects.filter(username=self.username).exists():
            return User.objects.get(username=self.username)

        user = User(username=self.username, email=self.email)
        user.set_password(self.password)
        user.save()
        return user

    def test_tos_validation(self):
        self.get('/accounts/register/')

        self.wait_for_textbox_then_type('[name="username"]', 'test')
        self.wait_for_textbox_then_type('[name="email"]', 'test@aol.com')
        self.wait_for_textbox_then_type('[name="password1"]', 'banana')
        self.wait_for_textbox_then_type('[name="password2"]', 'banana')

        self.click('form input[type="submit"]')

        self.wait_for_text("You must agree to the terms to register")

    def test_password_validation(self):
        self.get('/accounts/register/')

        self.wait_for_textbox_then_type('[name="username"]', 'test')
        self.wait_for_textbox_then_type('[name="email"]', 'test@aol.com')
        self.wait_for_textbox_then_type('[name="password1"]', 'banana')
        self.wait_for_textbox_then_type('[name="password2"]', 'apple')
        self.click('[name="tos"]')

        self.click('form input[type="submit"]')

        self.wait_for_text("The two password fields didn't match")

    def test_registration(self):
        self.get('/accounts/register/')

        self.wait_for_textbox_then_type('[name="username"]', self.username)
        self.wait_for_textbox_then_type('[name="email"]', self.email)
        self.wait_for_textbox_then_type('[name="password1"]', self.password)
        self.wait_for_textbox_then_type('[name="password2"]', self.password)
        self.click('[name="tos"]')
        self.click('[name="age_over_13"]')

        self.click('form input[type="submit"]')

        self.wait_for_text("check your email")

        self.assertEqual(mail.outbox[0].subject,
                         "Account activation on NYC TreesCount!")

        activation_link = self._get_link_from_email(mail.outbox[0])

        self.sel.get(activation_link)

        user = User.objects.get(username=self.username)
        self.assertEqual(self.username, user.username)
        self.assertEqual(self.email, user.email)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_minor)

        # Clear the test inbox
        mail.outbox = []

    def test_registration_as_minor(self):
        self.get('/accounts/register/')

        username = 'test'
        email = 'test@aol.com'

        self.wait_for_textbox_then_type('[name="username"]', username)
        self.wait_for_textbox_then_type('[name="email"]', email)
        self.wait_for_textbox_then_type('[name="password1"]', 'banana')
        self.wait_for_textbox_then_type('[name="password2"]', 'banana')
        self.click('[name="tos"]')

        # Omit clicking "I am over 13 years old" checkbox.

        self.click('form input[type="submit"]')

        self.wait_for_text("check your email")

        self.assertEqual(mail.outbox[0].subject,
                         "Account activation on NYC TreesCount!")

        activation_link = self._get_link_from_email(mail.outbox[0])

        self.sel.get(activation_link)

        user = User.objects.get(username=username)
        self.assertEqual(username, user.username)
        self.assertEqual(email, user.email)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_minor)

        # Clear the test inbox
        mail.outbox = []

    def test_forgot_username(self):
        self._get_or_create_user()
        self.get(reverse('forgot_username'))

        # Check that server-side validation works
        self.wait_for_textbox_then_type('[name="email"]', '')
        self.click('form input[type="submit"]')
        self.wait_for_text('This field is required')

        self.wait_for_textbox_then_type('[name="email"]', self.email)
        self.click('form input[type="submit"]')
        self.wait_for_text('Please check your email')

        self.assertEqual(mail.outbox[0].subject, "Account Recovery")
        self.assertRegexpMatches(mail.outbox[0].body, self.username)

    def test_login(self):
        self._get_or_create_user()
        self.get('/accounts/login/')

        self.wait_for_textbox_then_type('[name="username"]', self.username)
        self.wait_for_textbox_then_type('[name="password"]', self.password)

        self.click('form input[type="submit"]')

        self.wait_for_text('Contributions')
        expected_url = (self.live_server_url +
                        reverse('user_detail',
                                kwargs={'username': self.username}))
        self.assertEqual(expected_url, self.sel.current_url)

    def test_full_workflow(self):
        # Altogether now: register, recover username, then login
        # Each test uses _get_or_create_user for this purpose
        self.test_registration()
        self.test_forgot_username()
        self.test_login()


class PasswordResetUITest(NycUITest):
    def setUp(self):
        super(PasswordResetUITest, self).setUp()
        self.user = User.objects.create(username='Fry',
                                        email='fry@planetexpress.com')
        self.user.set_password('password')
        self.user.save()

    def _assert_reset_email_sent(self, value):
        self.get(reverse('password_reset'))
        self.wait_for_textbox_then_type('input[name="email_or_username"]',
                                        value)
        self.click('form input[type="submit"]')
        self.wait_for_text('We have sent you an email')
        self._get_link_from_email(mail.outbox[0])
        # TODO: Calling self.get with the link in the password reset
        # Email results in an exception being thrown inside the
        # WebDriver stack with the message "f.QueryInterface is not a
        # function." The URLs look correct, the registration tests,
        # which also follow URLs from emails pass, and the feature
        # works when exercised manually. It would be nice to fully
        # cover the reset workflow.

    def test_reset_with_email(self):
        self._assert_reset_email_sent(self.user.email)

    def test_reset_with_username(self):
        self._assert_reset_email_sent(self.user.username)
