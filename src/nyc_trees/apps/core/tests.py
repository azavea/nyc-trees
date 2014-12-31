# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.test import TestCase
from django.core.exceptions import ValidationError

from apps.core.models import User, Group


class UserModelTest(TestCase):
    def test_email_uniqueness(self):
        guy = User(username='guy', email='person@person.com')
        guy.set_password('password')
        guy.save()

        gal = User(username='gal', email='person@person.com')
        gal.set_password('password')

        with self.assertRaises(ValidationError) as ec:
            gal.clean_and_save()

        self.assertIn('email', ec.exception.error_dict)


class UserPrivacyTest(TestCase):
    def assert_clean_raises_validation_error(self, model, field):
        try:
            model.clean()
            self.fail('Expected clean to raise a ValidationError')
        except ValidationError as ve:
            self.assertTrue(field in ve.message_dict,
                            'Expected the message_dict of the ValidationError '
                            'to contain %s' % field)

    def test_minor_cant_make_profile_public(self):
        kid = User(is_minor=True, profile_is_public=True)
        self.assert_clean_raises_validation_error(kid, 'profile_is_public')

    def test_minor_cant_make_real_name_public(self):
        kid = User(is_minor=True, real_name_is_public=True)
        self.assert_clean_raises_validation_error(kid, 'real_name_is_public')

    def test_minor_cant_make_group_follows_public(self):
        kid = User(is_minor=True, group_follows_are_public=True)
        self.assert_clean_raises_validation_error(kid,
                                                  'group_follows_are_public')

    def test_minor_cant_make_contributions_public(self):
        kid = User(is_minor=True, contributions_are_public=True)
        self.assert_clean_raises_validation_error(kid,
                                                  'contributions_are_public')

    def test_minor_cant_make_achievements_public(self):
        kid = User(is_minor=True, achievements_are_public=True)
        self.assert_clean_raises_validation_error(kid,
                                                  'achievements_are_public')


class GroupModelTest(TestCase):
    def test_slugification(self):
        user = User.objects.create(username='hfarnesworth',
                                   email='prof@planetexpress.nyc',
                                   password='password')
        group = Group(
            name='Planet Express',
            admin=user,
            contact_email='info@planetexpress.com',
            contact_url='https://planetexpress.nyc',
            image='./photo.png'
        )
        group.clean_and_save()

        self.assertEqual('planet-express', group.slug)
