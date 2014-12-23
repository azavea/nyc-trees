# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.core.urlresolvers import reverse

from libs.ui_test_helpers import NycTreesSeleniumTestCase

from apps.core.models import User, Group


class GroupUITest(NycTreesSeleniumTestCase):
    def setUp(self):
        super(GroupUITest, self).setUp()
        self.public_user = User.objects.create(
            username='public_user',
            email='public_user@foo.com'
        )
        self.public_user.set_password('password')
        self.public_user.clean_and_save()

        self.census_admin_user = User.objects.create(
            username='census_admin_user',
            email='census_admin_user@foo.com',
            is_census_admin=True
        )
        self.census_admin_user.set_password('password')
        self.census_admin_user.clean_and_save()

        self.group_admin_user = User.objects.create(
            username='group_admin_user',
            email='group_admin_user@foo.com'
        )
        self.group_admin_user.set_password('password')
        self.group_admin_user.clean_and_save()

        self.group = Group.objects.create(
            name='The Best Group of All',
            description='Seriously, the best group in town.',
            slug='the-best-group',
            contact_info='Jane Best',
            contact_email='best@group.com',
            contact_url='https://thebest.nyc',
            admin=self.group_admin_user
        )

    @property
    def group_url(self):
        return reverse('group_detail', kwargs={
            'group_slug': self.group.slug
        })

    @property
    def group_edit_url(self):
        return reverse('group_edit', kwargs={
            'group_slug': self.group.slug
        })

    def test_anonymous_user_can_see_group_page(self):
        self.get(self.group_url)
        self.wait_for_text(self.group.name)

    def test_anonymous_user_redirected_when_getting_group_edit_page(self):
        self.get(self.group_edit_url)
        self.wait_for_text('Password:')

    def test_public_user_cannot_see_edit_form(self):
        self.login(self.public_user.username)
        self.get(self.group_edit_url)
        self.wait_for_text('Forbidden')

    def test_group_admin_can_see_edit_form(self):
        self.login(self.group_admin_user.username)
        self.get(self.group_edit_url)
        self.wait_for_element('textarea[name="description"]')

    def test_census_admin_can_see_edit_form(self):
        self.login(self.census_admin_user.username)
        self.get(self.group_edit_url)
        self.wait_for_element('textarea[name="description"]')
