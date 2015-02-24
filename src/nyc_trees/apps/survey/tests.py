# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import json
from datetime import timedelta

from django.contrib.gis.geos import LineString, MultiLineString
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import HttpResponseBadRequest
from django.test import TestCase
from django.utils.timezone import now

from apps.core.models import User, Group
from apps.core.test_utils import (make_request, make_tree, tree_defaults,
                                  make_survey, survey_defaults)

from apps.users.models import TrustedMapper

from apps.survey.models import (Blockface, BlockfaceReservation, Territory,
                                Survey, Tree)
from apps.survey.views import confirm_blockface_reservations, submit_survey


class SurveyTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='pat',
            password='password',
            email='pat@rat.com',
            first_name='Pat',
            last_name='Smith',
            profile_is_public=True,
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
        self.assertIn('blockfaces_requested', context)
        self.assertIn('blockfaces_reserved', context)
        self.assertIn('expiration_date', context)
        self.assertEqual(num, context['blockfaces_reserved'])

    def test_can_reserve_available_block(self):
        self.assert_blocks_reserved(1, self.block)

        reservation = BlockfaceReservation.objects.get(blockface=self.block)
        self.assertEqual(self.user.pk, reservation.user_id)

    def test_already_reserved(self):
        self.assert_blocks_reserved(1, self.block)

        reservation = BlockfaceReservation.objects.get(blockface=self.block)
        self.assertEqual(self.user.pk, reservation.user_id)

        self.assert_blocks_reserved(1, self.block, self.block2)

        self.assertEqual(1, BlockfaceReservation.objects
                         .filter(blockface=self.block).count())
        self.assertEqual(self.user.pk, reservation.user_id)

        reservation = BlockfaceReservation.objects.get(blockface=self.block2)
        self.assertEqual(self.user.pk, reservation.user_id)

    def test_reserve_trusted_mapper_blocks(self):
        group = Group.objects.create(
            name='The Best Group of All',
            description='Seriously, the best group in town.',
            slug='the-best-group',
            contact_name='Jane Best',
            contact_email='best@group.com',
            contact_url='https://thebest.nyc',
            admin=self.other_user
        )
        Territory.objects.create(group=group, blockface=self.block)

        self.assert_blocks_reserved(0, self.block)

        TrustedMapper.objects.create(group=group, user=self.user,
                                     is_approved=True)

        self.assert_blocks_reserved(01, self.block)
