# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.gis.geos import LineString
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.test import TestCase

from apps.core.models import User, Group
from apps.core.test_utils import make_request

from apps.survey.models import Tree, Species, Blockface, Survey

from apps.users.models import (Follow, Achievement, achievements,
                               AchievementDefinition)
from apps.users.views.user import user_detail as user_detail_view
from apps.users.routes.user import user_detail as user_detail_route
from apps.users.routes.group import (group_detail, group_edit,
                                     follow_group, unfollow_group)


class UsersTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='pat',
            password='password',
            email='pat@rat.com',
            first_name='Pat',
            last_name='Smith',
            profile_is_public=True,
        )
        self.other_user = User.objects.create(username='other', password='a')
        self.group = Group.objects.create(
            name='The Best Group of All',
            description='Seriously, the best group in town.',
            slug='the-best-group',
            contact_name='Jane Best',
            contact_email='best@group.com',
            contact_url='https://thebest.nyc',
            admin=self.other_user
        )
        Follow.objects.create(group=self.group, user=self.user)
        self.achievement = Achievement.objects.create(
            user=self.user,
            achievement_id=AchievementDefinition.FINISH_TRAINING
        )


class ProfileTemplateTests(UsersTestCase):
    def _update_user(self, **kwargs):
        User.objects.filter(pk=self.user.pk).update(**kwargs)

    def _render_profile(self, its_me):
        viewer = self.user if its_me else self.other_user
        request = make_request(user=viewer)
        return user_detail_route(request, self.user.username)

    def _assert_profile_contains(self, text, its_me=True, count=1):
        response = self._render_profile(its_me)
        self.assertContains(response, text, count=count)

    def _assert_profile_does_not_contain(self, text, its_me=True):
        response = self._render_profile(its_me)
        self.assertContains(response, text, count=0)

    def _assert_visible_to_all(self, text, me_count=1, them_count=1):
        self._assert_profile_contains(text, count=me_count)
        self._assert_profile_contains(text, its_me=False, count=them_count)

    def _assert_visible_only_to_me(self, text, count=1):
        self._assert_profile_contains(text, count=count)
        self._assert_profile_does_not_contain(text, its_me=False)

    def test_private_profile_404_if_not_me(self):
        self._update_user(profile_is_public=False)
        with self.assertRaises(Http404):
            self._render_profile(its_me=False)

    def test_username_visibility(self):
        self._assert_visible_only_to_me('Pat Smith')
        self._update_user(real_name_is_public=True)
        self._assert_visible_to_all('Pat Smith')

    def test_individual_mapper_not_shown_by_default(self):
        self._assert_profile_does_not_contain('Tree Mapper')

    def test_individual_mapper_visible_to_all(self):
        self._update_user(individual_mapper=True)
        self._assert_visible_to_all('Tree Mapper')

    def test_privacy_link_visible_only_to_me(self):
        self._assert_visible_only_to_me('Privacy</a>', count=1)

    def test_groups_section_visibility(self):
        self._assert_visible_only_to_me('<section class="groups">', count=1)
        self._update_user(group_follows_are_public=True)
        self._assert_visible_to_all('<section class="groups">',
                                    me_count=1,
                                    them_count=1)

    def test_groups_section_contents(self):
        self._assert_visible_only_to_me(self.group.name)
        self._update_user(group_follows_are_public=True)
        self._assert_visible_to_all(self.group.name)

    def test_achievements_section_visibility(self):
        self._assert_visible_only_to_me('<section class="achievements">',
                                        count=1)
        self._update_user(achievements_are_public=True)
        self._assert_visible_to_all('<section class="achievements">',
                                    me_count=1,
                                    them_count=1)

    def test_achievements_section_contents(self):
        self._assert_visible_only_to_me(
            achievements[AchievementDefinition.FINISH_TRAINING].name)
        self._update_user(achievements_are_public=True)
        self._assert_visible_to_all(
            achievements[AchievementDefinition.FINISH_TRAINING].name)

    def test_contributions_section_visibility(self):
        self._assert_visible_only_to_me('Contributions', count=2)
        self._update_user(contributions_are_public=True)
        self._assert_visible_to_all('Contributions', me_count=2, them_count=1)

    def test_contributions_section_contents(self):
        blockface = Blockface.objects.create(
            geom=LineString(((0, 0), (1, 1)))
        )
        species = Species.objects.create(name='Elm')
        survey = Survey.objects.create(
            blockface=blockface,
            user=self.user
        )
        Tree.objects.create(survey=survey, species=species)
        Tree.objects.create(survey=survey, species=species)

        request = make_request(user=self.user)
        context = user_detail_view(request, self.user.username)

        self.assertIn('counts', context)
        self.assertEqual(context['counts']['block'], 1)
        self.assertEqual(context['counts']['tree'], 2)
        self.assertEqual(context['counts']['species'], 1)


class GroupTemplateTests(UsersTestCase):
    def _render_detail(self):
        viewer = self.user
        request = make_request(user=viewer)
        return group_detail(request, self.group.slug)

    def _assert_group_detail_contains(self, text, count=1):
        response = self._render_detail()
        self.assertContains(response, text, count=count)

    def test_name_shown(self):
        self._assert_group_detail_contains(self.group.name)

    def test_description_shown(self):
        self._assert_group_detail_contains(self.group.description)

    def test_contact_shown(self):
        self._assert_group_detail_contains(self.group.contact_name)

    def test_url_shown(self):
        # The url shows up both as the link text and the href
        self._assert_group_detail_contains(self.group.contact_url, count=2)


class GroupAccessTests(UsersTestCase):
    def setUp(self):
        super(GroupAccessTests, self).setUp()
        self.census_admin = User.objects.create(
            username='censusadmin',
            password='password',
            email='ca@rat.com',
            first_name='Census',
            last_name='Admin',
            is_census_admin=True
        )

    def test_group_admin_can_get_group_edit_form(self):
        request = make_request(user=self.group.admin)
        response = group_edit(request, self.group.slug)
        self.assertTrue(response is not None)

    def test_group_admin_can_post_group_edit_form(self):
        request = make_request(user=self.group.admin, method="POST")
        response = group_edit(request, self.group.slug)
        self.assertTrue(response is not None)

    def test_census_admin_can_get_group_edit_form(self):
        request = make_request(user=self.census_admin)
        response = group_edit(request, self.group.slug)
        self.assertTrue(response is not None)

    def test_census_admin_can_post_group_edit_form(self):
        request = make_request(user=self.census_admin, method="POST")
        response = group_edit(request, self.group.slug)
        self.assertTrue(response is not None)

    def test_public_user_cannot_get_group_edit_form(self):
        request = make_request(user=self.user)
        self.assertRaises(PermissionDenied, group_edit, request,
                          self.group.slug)

    def test_public_user_cannot_post_group_edit_form(self):
        request = make_request(user=self.user, method="POST")
        self.assertRaises(PermissionDenied, group_edit, request,
                          self.group.slug)


class FollowGroupTests(UsersTestCase):
    def setUp(self):
        super(FollowGroupTests, self).setUp()
        Follow.objects.all().delete()

    def _is_following(self):
        return Follow.objects.filter(user=self.user, group=self.group) \
            .exists()

    def test_can_follow(self):
        self.assertFalse(self._is_following())

        request = make_request(user=self.user, method='POST')

        follow_group(request, self.group.slug)
        self.assertTrue(self._is_following())

        unfollow_group(request, self.group.slug)
        self.assertFalse(self._is_following())
