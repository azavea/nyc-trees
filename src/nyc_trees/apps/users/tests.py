# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from datetime import timedelta
from waffle.models import Flag

from django.contrib.auth.models import AnonymousUser
from django.contrib.gis.geos import LineString, MultiLineString

from django.core import mail
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.timezone import now

from apps.core.models import User, Group
from apps.core.test_utils import (make_request, make_event, make_tree,
                                  make_survey, make_species,
                                  complete_online_training, survey_defaults)

from apps.event.models import EventRegistration
from apps.event.routes import event_registration, check_in_user_to_event

from apps.survey.models import Blockface, Territory, Survey

from apps.users.models import (Follow, Achievement, achievements,
                               AchievementDefinition, TrustedMapper,
                               update_achievements)
from apps.users.views.user import user_detail as user_detail_view
from apps.users.views.group import group_detail as group_detail_view

from apps.home.routes import home_page
from apps.users.routes.user import (user_detail as user_detail_route,
                                    request_individual_mapper_status)
from apps.users.routes.group import (group_detail, group_edit,
                                     follow_group, unfollow_group,
                                     request_mapper_status,
                                     edit_user_mapping_priveleges)


class UsersTestCase(TestCase):
    def setUp(self):
        Flag.objects.create(name='full_access', everyone=True)

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
            admin=self.other_user,
            allows_individual_mappers=True
        )
        Follow.objects.create(group=self.group, user=self.user)


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
        self._assert_profile_contains('Privacy</a>', count=1)
        self._assert_profile_contains('Privacy</a>', count=0, its_me=False)

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

        # The achievements section is only publicly visible when that user
        # has earned an achievement
        self._update_user(achievements_are_public=True)
        self._assert_visible_only_to_me('<section class="achievements">',
                                        count=1)

        self.achievement = Achievement.objects.create(
            user=self.user,
            achievement_id=AchievementDefinition.ONLINE_TRAINING
        )
        self._assert_visible_to_all('<section class="achievements">',
                                    me_count=1,
                                    them_count=1)

    def test_achievements_section_contents(self):
        self.achievement = Achievement.objects.create(
            user=self.user,
            achievement_id=AchievementDefinition.ONLINE_TRAINING
        )
        self._assert_visible_only_to_me(
            achievements[AchievementDefinition.ONLINE_TRAINING].name)
        self._update_user(achievements_are_public=True)
        self._assert_visible_to_all(
            achievements[AchievementDefinition.ONLINE_TRAINING].name)

    def test_contributions_section_visibility(self):
        self._assert_visible_only_to_me('Contributions', count=2)
        self._update_user(contributions_are_public=True)
        self._assert_visible_to_all('Contributions', me_count=2, them_count=1)

    def test_contributions_section_contents(self):
        blockface = Blockface.objects.create(
            geom=MultiLineString(LineString(((0, 0), (1, 1))))
        )
        elm = make_species(common_name='Elm')
        maple = make_species(common_name='Maple')
        survey = make_survey(self.user, blockface)
        make_tree(survey, species=maple)
        make_tree(survey, species=elm)

        # Only the most recent survey for each block should be counted,
        # so all of the above data should *not* be reflected in the results
        other_survey = make_survey(self.user, blockface)
        make_tree(other_survey, species=elm)
        make_tree(other_survey)
        make_tree(other_survey)

        request = make_request(user=self.user)
        context = user_detail_view(request, self.user.username)

        self.assertIn('counts', context)
        self.assertEqual(context['counts']['block'], 1)
        self.assertEqual(context['counts']['tree'], 3)
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


class GroupDetailViewTests(UsersTestCase):
    def _assert_count_equals(self, name, num):
        req = make_request(user=self.user)
        req.group = self.group
        context = group_detail_view(req)

        self.assertEqual(num, context['counts'][name])

    def test_group_blocks_count(self):
        # We should default to 0%, even when the group has no territory
        self._assert_count_equals('block', '0.0%')

        block1 = Blockface.objects.create(
            geom=MultiLineString(LineString(((0, 0), (1, 1))))
        )
        block2 = Blockface.objects.create(
            geom=MultiLineString(LineString(((2, 2), (3, 3))))
        )
        Territory.objects.create(blockface=block1, group=self.group)
        Territory.objects.create(blockface=block2, group=self.group)

        make_survey(self.user, block1)

        # Until the blockface is no longer avialable, it doesn't count
        self._assert_count_equals('block', '0.0%')

        block1.is_available = False
        block1.save()

        self._assert_count_equals('block', '50.0%')

    def test_tree_count(self):
        # We start with 0 trees
        self._assert_count_equals('tree_digits',
                                  ['0', '0', '0', '0', '0', '0', '0'])

        block1 = Blockface.objects.create(
            geom=MultiLineString(LineString(((0, 0), (1, 1))))
        )
        Territory.objects.create(blockface=block1, group=self.group)

        survey = make_survey(self.user, block1)
        make_tree(survey)
        make_tree(survey)

        # Once we add a survey, we should see some tree counts
        self._assert_count_equals('tree_digits',
                                  ['0', '0', '0', '0', '0', '0', '2'])

        other_survey = make_survey(self.user, block1)
        make_tree(other_survey)
        make_tree(other_survey)
        make_tree(other_survey)

        # Only the most recent survey for each block should be counted,
        # so the count should go to 3, not 5
        self._assert_count_equals('tree_digits',
                                  ['0', '0', '0', '0', '0', '0', '3'])

    def test_events_count(self):
        week_ago = now() - timedelta(days=7)
        almost_week_ago = week_ago + timedelta(hours=1)

        next_week = now() + timedelta(days=7)
        almost_next_week = next_week - timedelta(hours=1)

        make_event(self.group, begins_at=week_ago, ends_at=almost_week_ago,
                   title='event 1')
        make_event(self.group, begins_at=almost_next_week, ends_at=next_week,
                   title='event 2')

        self._assert_count_equals('event', 1)

    def test_attendees_count(self):
        week_ago = now() - timedelta(days=7)
        almost_week_ago = week_ago + timedelta(hours=1)

        next_week = now() + timedelta(days=7)
        almost_next_week = next_week - timedelta(hours=1)

        past_event = make_event(self.group, begins_at=week_ago,
                                ends_at=almost_week_ago, title='event 1')
        other_past_event = make_event(self.group, begins_at=week_ago,
                                      ends_at=almost_week_ago, title='event 2')
        future_event = make_event(self.group, begins_at=almost_next_week,
                                  ends_at=next_week, title='event 3')

        EventRegistration.objects.create(event=past_event, user=self.user,
                                         did_attend=True)
        EventRegistration.objects.create(event=other_past_event,
                                         user=self.user, did_attend=True)

        # Users are double counted for event attendence
        self._assert_count_equals('attendees', 2)

        EventRegistration.objects.create(event=other_past_event,
                                         user=self.other_user)
        # We don't count users who were not checked in to the event
        self._assert_count_equals('attendees', 2)

        # We don't count future events
        EventRegistration.objects.create(event=future_event,
                                         user=self.other_user, did_attend=True)
        self._assert_count_equals('attendees', 2)

        EventRegistration.objects.create(event=past_event,
                                         user=self.other_user, did_attend=True)
        self._assert_count_equals('attendees', 3)


class GroupAccessTests(UsersTestCase):
    def setUp(self):
        super(GroupAccessTests, self).setUp()
        self.census_admin = User.objects.create(
            username='censusadmin',
            password='password',
            email='ca@rat.com',
            first_name='Census',
            last_name='Admin',
            is_superuser=True
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


class IndividualMapperTests(UsersTestCase):
    """Test that users can become individual mappers"""

    def setUp(self):
        super(IndividualMapperTests, self).setUp()
        self.mapping_event = make_event(self.group,
                                        title='Mapping event',
                                        slug='mapping-event',
                                        includes_training=False)
        self.training_event = make_event(self.group,
                                         title='Training event',
                                         slug='training-event',
                                         includes_training=True)

    def _become_individual_mapper(self):
        # Is the button visible on the user profile page?
        request = make_request(user=self.user)
        response = user_detail_route(request, username=self.user.username)
        self.assertTrue('Request Individual Mapper Status' in response.content)

        # Is the button visible on the dashboard?
        request = make_request(user=self.user)
        response = home_page(request)
        content = response.content.decode('utf8')
        self.assertTrue('Request Individual Mapper Status' in content)

        # Press the button.
        request = make_request(user=self.user, method='POST')
        response = request_individual_mapper_status(
            request,
            username=self.user.username)
        # This request should redirect to the instructions page upon success.
        self.assertIs(type(response), HttpResponseRedirect)

    def _rsvp_to_event(self, event):
        mail.outbox = []
        request = make_request(user=self.user, method='POST')
        response = event_registration(request, group_slug=self.group.slug,
                                      event_slug=event.slug)
        self.assertEqual(1, len(mail.outbox), "Expected RSVP to send an email")
        self.assertTrue('data-verb="DELETE"' in response.content)

    def _checkin_to_event(self, event):
        request = make_request(user=self.other_user, method='POST')
        response = check_in_user_to_event(request, group_slug=self.group.slug,
                                          event_slug=event.slug,
                                          username=self.user.username)
        self.assertTrue('data-verb="DELETE"' in response.content)

    # This test asserts that an email is sent when RSVPing to an
    # event. Because the email is sent via a Celery task, we use
    # CELERY_ALWAYS_EAGER to force synchronous execution and ensure
    # the assertion is made after the task is complete.
    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_individual_mapper_workflow(self):
        self.assertFalse(self.user.individual_mapper)
        self.assertFalse(self.user.field_training_complete)
        self.assertFalse(self.user.online_training_complete)
        self.assertFalse(self.user.eligible_to_become_individual_mapper())
        self.assertRaises(AssertionError, self._become_individual_mapper)
        self.assertRaises(PermissionDenied,
                          self._rsvp_to_event, self.training_event)

        complete_online_training(self.user)

        self.user = User.objects.get(id=self.user.id)
        self.assertTrue(self.user.online_training_complete)
        self.assertFalse(self.user.eligible_to_become_individual_mapper())

        self._rsvp_to_event(self.training_event)
        self._checkin_to_event(self.training_event)

        self.user = User.objects.get(id=self.user.id)
        self.assertTrue(self.user.field_training_complete)
        self.assertTrue(self.user.training_complete)
        self.assertFalse(self.user.eligible_to_become_individual_mapper())

        self._rsvp_to_event(self.mapping_event)
        self._checkin_to_event(self.mapping_event)

        self.user = User.objects.get(id=self.user.id)
        self.assertTrue(self.user.eligible_to_become_individual_mapper())

        self._become_individual_mapper()

        self.user = User.objects.get(id=self.user.id)
        self.assertTrue(self.user.individual_mapper)
        self.assertFalse(self.user.eligible_to_become_individual_mapper())


class TrustedMapperTests(UsersTestCase):
    """Test that users can become trusted mappers"""

    def _become_trusted_mapper(self):
        user, group = self.user, self.group

        # Does the grant access button appear on the group detail page?
        request = make_request(user=user)
        response = group_detail(request, group_slug=group.slug)
        self.assertTrue('Request Individual Mapper Status' in response.content)

        # User request mapper status
        request = make_request(user=user, method='POST')
        request_mapper_status(request, group_slug=group.slug)

        # Clear the test inbox
        mail.outbox = []

        # Group admin approve mapper status
        request = make_request(user=group.admin, method='PUT')
        response = edit_user_mapping_priveleges(request,
                                                group_slug=group.slug,
                                                username=user.username)
        self.assertEqual(1, len(mail.outbox),
                         'Expected approving a trusted mapper to send an '
                         'email')
        self.assertTrue('btn-approve' in response.content)

    def _is_eligible(self):
        return self.user.eligible_to_become_trusted_mapper(self.group)

    def test_trusted_mapper_workflow(self):
        """
        First, disqualify user from becoming a trusted mapper.
        Then enable each qualification, one by one, to ensure that all
        conditions must be met before becoming eligible.
        Finally, after successfully becoming an individual mapper, ensure
        that the user is no longer eligible.
        """
        self.group.allows_individual_mappers = False
        self.group.admin = self.user
        self.group.clean_and_save()
        self.user.individual_mapper = False
        self.user.clean_and_save()
        TrustedMapper.objects.create(group=self.group, user=self.user,
                                     is_approved=True)
        self.assertFalse(self._is_eligible())

        self.group.allows_individual_mappers = True
        self.group.clean_and_save()
        self.assertFalse(self._is_eligible())

        self.group.admin = self.other_user
        self.group.clean_and_save()
        self.assertFalse(self._is_eligible())

        TrustedMapper.objects.all().delete()
        self.assertFalse(self._is_eligible())

        self.user.individual_mapper = True
        self.assertTrue(self._is_eligible())

        self._become_trusted_mapper()
        self.assertFalse(self._is_eligible())


class AnonUserTests(UsersTestCase):
    """Test that public facing pages are viewable to logged out users"""

    def setUp(self):
        super(AnonUserTests, self).setUp()
        self.anon_user = AnonymousUser()

    def _test_does_not_throw(self, view_fn, *args):
        try:
            request = make_request(user=self.anon_user)
            response = view_fn(request, *args)
            return response
        except Exception as ex:
            self.fail(ex)

    def test_group_detail_visible(self):
        self._test_does_not_throw(group_detail, self.group.slug)


class AchievementTests(UsersTestCase):
    def setUp(self):
        super(AchievementTests, self).setUp()

    def _assertAchievements(self, expected_ids):
        update_achievements(self.user)
        achieved_ids = set([a.achievement_id
                            for a in self.user.achievement_set.all()])
        self.assertEqual(set(expected_ids), achieved_ids)

    def testGroupFollows(self):
        self._assertAchievements([])
        for i in range(0, 5):
            group = Group.objects.create(name=str(i), slug=str(i))
            Follow.objects.create(group=group, user=self.user)
        self._assertAchievements([AchievementDefinition.FOLLOW_GROUPS])

    def testOnlineTraining(self):
        self._assertAchievements([])
        complete_online_training(self.user)
        self._assertAchievements([AchievementDefinition.ONLINE_TRAINING])

    def testTrainingEvent(self):
        self._assertAchievements([])
        self.user.field_training_complete = True
        self._assertAchievements([AchievementDefinition.TRAINING_EVENT])

    def testMappingEvent(self):
        self._assertAchievements([])
        for i in range(0, 2):
            event = make_event(self.group, title=unicode(i))
            EventRegistration.objects.create(event=event, user=self.user,
                                             did_attend=True)
        self._assertAchievements([AchievementDefinition.MAPPING_EVENT])

    def test50Blocks(self):
        self._assertAchievements([])
        geom = MultiLineString(LineString(((0, 0), (1, 1))))
        blocks = [Blockface(geom=geom) for i in range(0, 100)]
        Blockface.objects.bulk_create(blocks)

        surveys = []
        s = survey_defaults()
        for b in Blockface.objects.all():
            s.update(user=self.user, blockface=b)
            surveys.append(Survey(**s))
        Survey.objects.bulk_create(surveys)

        self._assertAchievements([AchievementDefinition.MAP_50,
                                  AchievementDefinition.MAP_100])
