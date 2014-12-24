# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.core.urlresolvers import reverse

from libs.ui_test_helpers import NycTreesSeleniumTestCase

from apps.core.models import User, Group


class BaseGroupUITest(NycTreesSeleniumTestCase):
    def setUp(self):
        super(BaseGroupUITest, self).setUp()
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
    def group_list_url(self):
        return reverse('group_list_page')

    @property
    def group_edit_url(self):
        return reverse('group_edit', kwargs={
            'group_slug': self.group.slug
        })


class GroupUITest(BaseGroupUITest):
    def test_anonymous_user_can_see_group_page(self):
        self.get(self.group.get_absolute_url())
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


class FollowGroupUITest(BaseGroupUITest):
    def _click_follow(self):
        self.wait_for_text('Follow')
        self.click('.btn-follow')

    def _click_unfollow(self):
        self.wait_for_text('Following')
        self.click('.btn-unfollow')

    def test_anonymous_user_follow_redirect_on_group_list_page(self):
        self.get(self.group_list_url)
        self._click_follow()
        self.wait_for_text('Password:')

    def test_anonymous_user_follow_redirect_on_group_detail_page(self):
        self.get(self.group.get_absolute_url())
        self._click_follow()
        self.wait_for_text('Password:')

    def test_follow_on_group_list_page(self):
        self.login(self.public_user.username)
        self.get(self.group_list_url)
        self._click_follow()
        self._click_unfollow()
        self._click_follow()

    def test_follow_on_group_detail_page(self):
        self.login(self.public_user.username)
        self.get(self.group.get_absolute_url())
        self._click_follow()
        self._click_unfollow()
        self._click_follow()
