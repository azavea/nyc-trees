# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import os
import json
from datetime import timedelta
from waffle.models import Flag

from functools import partial

from django.contrib.gis.geos import LineString, MultiLineString
from django.conf import settings
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import connection
from django.http import HttpResponseBadRequest
from django.test import TestCase
from django.utils.timezone import now

from apps.core.models import User, Group
from apps.core.test_utils import (make_request, make_tree, tree_defaults,
                                  make_survey, survey_defaults, make_territory,
                                  make_trusted_mapper, make_reservation)

from apps.users import get_achievements_for_user
from apps.users.models import TrustedMapper, Achievement

from apps.survey.models import (Blockface, BlockfaceReservation, Territory,
                                Survey, Tree)
from apps.survey.views import confirm_blockface_reservations, submit_survey, \
    flag_survey


class SurveyTestCase(TestCase):
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
        self.other_user = User.objects.create(
            username='foo',
            password='password',
            email='foo@bar.com',
            first_name='Foo',
            last_name='Bar',
            profile_is_public=True,
        )
        self.group = Group.objects.create(
            name='The Best Group of All',
            description='Seriously, the best group in town.',
            slug='the-best-group',
            contact_name='Jane Best',
            contact_email='best@group.com',
            contact_url='https://thebest.nyc',
            admin=self.other_user
        )
        self.other_group = Group.objects.create(
            name='Another Group',
            description='Another Group description',
            slug='the-other-group',
            contact_name='Who Knows',
            contact_email='other@aol.com',
            contact_url='https://google.com',
            admin=self.other_user
        )
        self.block = Blockface.objects.create(
            geom=MultiLineString(LineString(((0, 0), (1, 1))))
        )
        self.survey_data = survey_defaults()
        self.survey_data['blockface_id'] = self.block.id


class TreeValidationTests(SurveyTestCase):
    def setUp(self):
        super(TreeValidationTests, self).setUp()
        self.survey = make_survey(self.user, self.block)

    def test_bad_problem(self):
        with self.assertRaises(ValidationError):
            make_tree(self.survey, problems='foo,bar')

    def test_duplicate_problem(self):
        with self.assertRaises(ValidationError):
            make_tree(self.survey, problems='Sneakers,Sneakers')


class SurveySubmitTests(SurveyTestCase):
    def setUp(self):
        super(SurveySubmitTests, self).setUp()
        next_week = now() + timedelta(days=7)
        BlockfaceReservation(user=self.user,
                             blockface=self.block,
                             is_mapping_with_paper=False,
                             expires_at=next_week
                             ).save()

    def submit_survey(self, survey_data, tree_data):
        body = json.dumps({
            'survey': survey_data,
            'trees': tree_data
        })
        req = make_request(user=self.user, body=body, method="POST")
        return submit_survey(req)

    def test_submit_success(self):
        tree_data = tree_defaults()
        tree_data['problems'] = ['Stones', 'Sneakers']

        self.submit_survey(self.survey_data, [tree_data, tree_data])

        survey = Survey.objects.all()[0]
        self.assertEqual(survey.blockface_id, self.block.id)
        self.assertEqual(survey.user_id, self.user.id)
        self.assertEqual(survey.is_left_side, False)

        trees = Tree.objects.all()
        self.assertEqual(len(trees), 2)
        tree = trees[0]
        self.assertEqual(tree.circumference, tree_data['circumference'])
        self.assertEqual(tree.health, tree_data['health'])
        self.assertEqual(tree.survey, survey)
        self.assertEqual(tree.problems, 'Stones,Sneakers')

    def test_missing_trees(self):
        error = self.submit_survey({'has_trees': True}, [])
        self.assertTrue(isinstance(error, HttpResponseBadRequest))

    def test_extra_trees(self):
        error = self.submit_survey({'has_trees': False}, [tree_defaults()])
        self.assertTrue(isinstance(error, HttpResponseBadRequest))

    def test_missing_blockface(self):
        with self.assertRaises(ObjectDoesNotExist):
            self.submit_survey({'has_trees': False}, [])

    def test_bad_survey_field(self):
        with self.assertRaises(TypeError):
            self.submit_survey({'has_trees': False, 'foo': 1}, [])

    def test_bad_tree_field(self):
        with self.assertRaises(TypeError):
            self.submit_survey(self.survey_data, [{'bar': 2}])

    def test_flag_survey(self):
        survey = make_survey(self.user, self.block)
        self.assertFalse(survey.is_flagged)
        req = make_request(user=self.user, method="POST")
        result = flag_survey(req, survey.id)
        self.assertTrue(result['success'])
        survey = Survey.objects.get(id=survey.id)
        self.assertTrue(survey.is_flagged)


class ConfirmBlockfaceReservationTests(SurveyTestCase):
    def setUp(self):
        super(ConfirmBlockfaceReservationTests, self).setUp()
        self.block2 = Blockface.objects.create(
            geom=MultiLineString(LineString(((2, 2), (3, 3))))
        )
        self.other_user = User.objects.create(username='other', password='a')

    def assert_blocks_reserved(self, num, *blocks):
        ids = ",".join(str(block.pk) for block in blocks)
        req = make_request(user=self.user, params={
            'ids': ids, 'is_mapping_with_paper': 'False'}, method="POST")

        context = confirm_blockface_reservations(req)
        self.assertIn('n_requested', context)
        self.assertIn('n_reserved', context)
        self.assertIn('expiration_date', context)
        self.assertEqual(num, context['n_reserved'])

    def test_can_reserve_available_block(self):
        self.assert_blocks_reserved(1, self.block)

        reservation = BlockfaceReservation.objects.get(blockface=self.block)
        self.assertEqual(self.user.pk, reservation.user_id)

    def test_already_reserved(self):
        self.assert_blocks_reserved(1, self.block)

        reservation = BlockfaceReservation.objects.get(blockface=self.block)
        self.assertEqual(self.user.pk, reservation.user_id)

        self.assert_blocks_reserved(1, self.block2)

        self.assertEqual(1, BlockfaceReservation.objects
                         .filter(blockface=self.block).count())
        self.assertEqual(self.user.pk, reservation.user_id)

        reservation = BlockfaceReservation.objects.get(blockface=self.block2)
        self.assertEqual(self.user.pk, reservation.user_id)

    def test_cancelling_blocks(self):
        self.assert_blocks_reserved(1, self.block)

        reservation = BlockfaceReservation.objects.get(blockface=self.block)
        self.assertEqual(self.user.pk, reservation.user_id)

        self.assert_blocks_reserved(1, self.block2)

        # Block just passed in is reserved
        self.assertEqual(1, BlockfaceReservation.objects
                         .filter(blockface=self.block2).current().count())
        self.assertEqual(self.user.pk, reservation.user_id)

        # Previously reserved block that was omitted is now cancelled
        self.assertEqual(0, BlockfaceReservation.objects
                         .filter(blockface=self.block).current().count())
        self.assertEqual(self.user.pk, reservation.user_id)

    def test_reserve_trusted_mapper_blocks(self):
        Territory.objects.create(group=self.group, blockface=self.block)

        self.assert_blocks_reserved(0, self.block)

        TrustedMapper.objects.create(group=self.group, user=self.user,
                                     is_approved=True)

        self.assert_blocks_reserved(01, self.block)


class TeammateTests(SurveyTestCase):
    def test_survey_achievements(self):
        self._assert_blockface_achievements(0, 0)
        self._assert_blockface_achievements(50, 1)
        self._assert_blockface_achievements(100, 2)
        self._assert_blockface_achievements(200, 3)
        self._assert_blockface_achievements(400, 4)
        self._assert_blockface_achievements(1000, 5)

    def _assert_blockface_achievements(self, amount_blockfaces,
                                       amount_achievements):
        Survey.objects.all().delete()
        Blockface.objects.all().delete()
        Achievement.objects.all().delete()

        # Add blocks
        Blockface.objects.bulk_create(
            Blockface(
                geom=MultiLineString(LineString(((0, 0), (1, 1)))),
                created_at=now())
            for i in xrange(amount_blockfaces))

        # Survey blocks (solo)
        ids = Blockface.objects.values_list('id', flat=True)
        Survey.objects.bulk_create(
            Survey(blockface_id=id,
                   user=self.user,
                   created_at=now(),
                   is_flagged=False,
                   has_trees=True,
                   is_left_side=True,
                   is_mapped_in_blockface_polyline_direction=True)
            for id in ids)

        # Assert first user (only) has achievements
        achievements = get_achievements_for_user(self.user)['achieved']
        self.assertEqual(amount_achievements, len(achievements))
        achievements = get_achievements_for_user(self.other_user)['achieved']
        self.assertEqual(0, len(achievements))

        # Survey blocks (with partner)
        Survey.objects.all().update(teammate=self.other_user)

        # Assert both users have achievements
        achievements = get_achievements_for_user(self.user)['achieved']
        self.assertEqual(amount_achievements, len(achievements))
        achievements = get_achievements_for_user(self.other_user)['achieved']
        self.assertEqual(amount_achievements, len(achievements))


class TilerTests(SurveyTestCase):
    def setUp(self):
        super(TilerTests, self).setUp()
        Survey.objects.all().delete()

    def _exec_tiler_query(self, filename, **kwargs):
        group_id = kwargs.get('group_id', 0)
        user_id = kwargs.get('user_id', 0)

        # All tiler queries are in the form "(...) AS query" which isn't
        # a valid query. We need to prepend a select to this subquery
        # to make it valid.
        query = 'SELECT * FROM '

        path = os.path.join(settings.TILER_SQL_PATH, filename)
        with open(path, 'r') as f:
            query += f.read()

        # Replace template placeholders.
        query = query.replace('<%= group_id %>', str(group_id))
        query = query.replace('<%= user_id %>', str(user_id))
        query = self._strip_invalid_lines(query)

        with connection.cursor() as cursor:
            cursor.execute(query)
            return dictfetchall(cursor)

    def _strip_invalid_lines(self, query):
        """
        Really basic line stripper to remove things that are not valid
        SQL syntax from the query.
        """
        result = []
        lines = (line.strip() for line in query.split('\n'))
        for line in lines:
            if line.startswith('<%'):
                continue
            result.append(line)
        return '\n'.join(result)

    def test_group_progress(self):
        query = partial(self._exec_tiler_query,
                        'group_progress.sql',
                        group_id=self.group.id)

        # Test that this group has no blocks yet.
        self.assertEqual(0, len(query()))

        # Test that adding a territory yields an unmapped block for this group.
        make_territory(self.group, self.block)
        rows = query()
        self.assertEqual(1, len(rows))
        self.assertEqual(rows[0]['is_mapped'], 'F')

        # Test that surveying the block yields a mapped block for this group.
        make_survey(self.user, self.block)
        rows = query()
        self.assertEqual(rows[0]['is_mapped'], 'T')

    def test_group_territory(self):
        query = partial(self._exec_tiler_query,
                        'group_territory.sql',
                        group_id=self.group.id)

        # Test that this group has no blocks yet.
        self.assertEqual(0, len(query()))

        # Test that all blocks in this group return 'reserved'.
        # TODO: Verify this is the correct behavior.
        make_territory(self.group, self.block)
        rows = query()
        self.assertEqual(1, len(rows))
        self.assertEqual(rows[0]['survey_type'], 'reserved')

    def test_group_territory_admin(self):
        query = partial(self._exec_tiler_query,
                        'group_territory_admin.sql',
                        group_id=self.group.id)

        ###
        # Test various scenarios when block is available.
        ###
        self.block.is_available = True
        self.block.save()

        # Test 'available' case.
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'available')

        # Test 'reserved' case.
        t = make_territory(self.group, self.block)
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'reserved')
        t.delete()

        # Test 'unavailable' case (owned by another territory).
        t = make_territory(self.other_group, self.block)
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'unavailable')
        t.delete()

        # Test 'unavailable' case (reserved by someone).
        make_reservation(self.user, self.block)
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'unavailable')

        ###
        # Test various scenarios when block is unavailable.
        ###
        self.block.is_available = False
        self.block.save()

        # Test 'suveyed-by-others' case.
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'surveyed-by-others')

        # Test 'surveyed-by-me' case.
        t = make_territory(self.group, self.block)
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'surveyed-by-me')
        t.delete()

    def test_group_territory_survey(self):
        query = partial(self._exec_tiler_query,
                        'group_territory_survey.sql',
                        group_id=self.group.id)

        # Test that this group has no blocks yet.
        self.assertEqual(0, len(query()))

        # Test that adding a territory returns the correct blocks.
        make_territory(self.group, self.block)
        rows = query()
        self.assertEqual(1, len(rows))

        # Test the 'unavailable' case.
        Blockface.objects.update(id=self.block.id, is_available=False)
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'unavailable')

        # Test the 'available' case.
        Blockface.objects.update(id=self.block.id, is_available=True)
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'available')

        # Test that reserving a block makes it unavailable.
        r = make_reservation(self.user, self.block)
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'unavailable')
        r.delete()

        # Test that an expired reservation makes the block available again.
        expires_at = now() - timedelta(days=1)
        r = make_reservation(self.user, self.block, expires_at=expires_at)
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'available')
        r.delete()

    def test_progress(self):
        query = partial(self._exec_tiler_query, 'progress.sql')

        # Test that all test blocks are returned initially.
        rows = query()
        self.assertEqual(1, len(rows))
        self.assertEqual(rows[0]['is_mapped'], 'F')

        # Test that adding a survey marks block as mapped.
        make_survey(self.user, self.block)
        rows = query()
        self.assertEqual(rows[0]['is_mapped'], 'T')

    def test_user_progress(self):
        query = partial(self._exec_tiler_query,
                        'user_progress.sql',
                        user_id=self.user.id)

        # Test that our initial block is present, but not mapped by this user.
        rows = query()
        self.assertEqual(1, len(rows))
        self.assertEqual(rows[0]['is_mapped'], 'F')

        # Test that adding a survey marks this block mapped by this user.
        s = make_survey(self.user, self.block)
        rows = query()
        self.assertEqual(rows[0]['is_mapped'], 'T')
        s.delete()

        # Test that we don't see progress from other users.
        s = make_survey(self.other_user, self.block)
        rows = query()
        self.assertEqual(rows[0]['is_mapped'], 'F')
        s.delete()

        # Test that user gets credit for being a teammate.
        s = make_survey(self.other_user, self.block, teammate=self.user)
        rows = query()
        self.assertEqual(rows[0]['is_mapped'], 'T')
        s.delete()

    def _test_user_reservations(self, query):
        """
        Basic tests that should pass on all queries that handle user
        reservations.
        """
        # Test that cancelled reservations don't appear.
        r = make_reservation(self.user, self.block, canceled_at=now())
        rows = query()
        self.assertEqual(0, len(rows))
        r.delete()

        # Test that expired reservations don't appear.
        expires_at = now() - timedelta(days=1)
        r = make_reservation(self.user, self.block, expires_at=expires_at)
        rows = query()
        self.assertEqual(0, len(rows))
        r.delete()

        # Test that other users' reservations don't appear in our results.
        r = make_reservation(self.other_user, self.block)
        rows = query()
        self.assertEqual(0, len(rows))
        r.delete()

    def test_user_reservable(self):
        query = partial(self._exec_tiler_query,
                        'user_reservable.sql',
                        user_id=self.user.id)

        # This is a prerequisite condition for other assertions in
        # this test to pass.
        self.assertEqual(self.group.admin, self.other_user)

        # Test that this shows all test blocks initially.
        self.assertEqual(1, len(query()))

        # Test 'available' case for free agent blocks (no territory and
        # and no reservation).
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'available')
        self.assertEqual(rows[0]['restriction'], 'none')

        # Test that group owned blocks (with independent mappers disabled)
        # are 'unavailable' by default.
        t = make_territory(self.group, self.block)
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'unavailable')
        self.assertEqual(rows[0]['restriction'], 'unavailable')
        t.delete()

        # Test that "expert group" blocks are 'unavailable' by default.
        self.group.is_active = False
        self.group.save()
        t = make_territory(self.group, self.block)
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'unavailable')
        self.assertEqual(rows[0]['restriction'], 'unavailable')
        t.delete()
        self.group.is_active = True
        self.group.save()

        # Test that group owned blocks are not available to trusted mappers
        # if the group does not allow trusted mappers.
        # TODO: Does it make sense for a block to be both available and
        # unavailable at the same time?
        t = make_territory(self.group, self.block)
        tr = make_trusted_mapper(self.user, self.group)
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'available')
        self.assertEqual(rows[0]['restriction'], 'unavailable')
        tr.delete()
        t.delete()

        # Test that group admins can reserve blocks in their territory.
        t = make_territory(self.group, self.block)
        r = make_reservation(self.other_user, self.block)
        rows = query(user_id=self.other_user.id)
        self.assertEqual(rows[0]['survey_type'], 'available')
        self.assertEqual(rows[0]['restriction'], 'none')
        r.delete()
        t.delete()

        # Test that group owned blocks are available to group admins.
        t = make_territory(self.group, self.block)
        rows = query(user_id=self.other_user.id)
        self.assertEqual(rows[0]['survey_type'], 'available')
        self.assertEqual(rows[0]['restriction'], 'none')
        t.delete()

        # Test that block is unavailable if someone else reserved it.
        t = make_territory(self.group, self.block)
        r = make_reservation(self.other_user, self.block)
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'unavailable')
        self.assertEqual(rows[0]['restriction'], 'unavailable')
        r.delete()
        t.delete()

        # Test that block is unavailable if someone else reserved it (as a
        # group admin).
        t = make_territory(self.group, self.block)
        r = make_reservation(self.user, self.block)
        rows = query(user_id=self.other_user.id)
        self.assertEqual(rows[0]['survey_type'], 'unavailable')
        self.assertEqual(rows[0]['restriction'], 'reserved')
        r.delete()
        t.delete()

        # Test that blocks are marked 'unavailable' when someone else has
        # reserved the block (when independent mappers are not enabled).
        t = make_territory(self.group, self.block)
        r = make_reservation(self.other_user, self.block)
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'unavailable')
        self.assertEqual(rows[0]['restriction'], 'unavailable')
        r.delete()
        t.delete()

        # Test that the block becomes unavailable when another user
        # has reserved it.
        r = make_reservation(self.other_user, self.block)
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'unavailable')
        self.assertEqual(rows[0]['restriction'], 'reserved')
        r.delete()

        # Test that the block is available if the current user has reserved it.
        r = make_reservation(self.user, self.block)
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'available')
        self.assertEqual(rows[0]['restriction'], 'none')
        r.delete()

        ###
        # This group will allow independent mappers from here on.
        ###
        self.group.allows_individual_mappers = True
        self.group.clean_and_save()

        # Test that blocks owned by groups (with individual mapping enabled)
        # are marked as 'group_territory' instead of 'unavailable'.
        t = make_territory(self.group, self.block)
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'unavailable')
        self.assertEqual(rows[0]['restriction'], 'group_territory')
        t.delete()

        # Test that group owned blocks are available to trusted mappers.
        t = make_territory(self.group, self.block)
        tr = make_trusted_mapper(self.user, self.group)
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'available')
        self.assertEqual(rows[0]['restriction'], 'none')
        tr.delete()
        t.delete()

        # Test that blocks are marked 'reserved' when someone else has
        # reserved it (when independent mappers are enabled).
        t = make_territory(self.group, self.block)
        r = make_reservation(self.other_user, self.block)
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'unavailable')
        self.assertEqual(rows[0]['restriction'], 'reserved')
        r.delete()
        t.delete()

        # Test that survey_type and restriction is unavailable if block has
        # been surveyed. This should take precendence over all other
        # restrictions.
        self.block.is_available = False
        self.block.save()
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'unavailable')
        self.assertEqual(rows[0]['restriction'], 'unavailable')
        self.block.is_available = True
        self.block.save()

    def test_user_reservations(self):
        query = partial(self._exec_tiler_query,
                        'user_reservations.sql',
                        user_id=self.user.id)

        # Test that this shows no blocks initially.
        self.assertEqual(0, len(query()))

        # Test that standard user reservations work.
        self._test_user_reservations(query)

        # Test 'available' case.
        r = make_reservation(self.user, self.block)
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'available')
        self.assertEqual(rows[0]['restriction'], 'none')
        r.delete()

        # Test 'unavailable' case.
        self.block.is_available = False
        self.block.save()
        r = make_reservation(self.user, self.block)
        rows = query()
        self.assertEqual(0, len(query()))
        r.delete()

    def test_user_reservations_print(self):
        query = partial(self._exec_tiler_query,
                        'user_reservations_print.sql',
                        user_id=self.user.id)

        # Test user has no blocks to start with.
        self.assertEqual(0, len(query()))

        # Test that standard user reservations work.
        self._test_user_reservations(query)

        # Test that adding a reservation marks the block as reserved.
        r = make_reservation(self.user, self.block)
        rows = query()
        self.assertEqual(rows[0]['survey_type'], 'reserved')
        r.delete()


# Source: https://docs.djangoproject.com/en/1.8/topics/db/sql/#executing-custom-sql-directly  # NOQA
def dictfetchall(cursor):
    """Returns all rows from a cursor as a dict"""
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]
