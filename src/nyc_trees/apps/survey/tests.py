# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.gis.geos import LineString, MultiLineString
from django.test import TestCase

from apps.core.models import User, Group
from apps.core.test_utils import make_request

from apps.users.models import TrustedMapper

from apps.survey.models import Blockface, BlockfaceReservation, Territory
from apps.survey.views import confirm_blockface_reservations


class ConfirmBlockfaceReservationTests(TestCase):
    def setUp(self):
        self.block1 = Blockface.objects.create(
            geom=MultiLineString(LineString(((0, 0), (1, 1))))
        )
        self.block2 = Blockface.objects.create(
            geom=MultiLineString(LineString(((2, 2), (3, 3))))
        )
        self.user = User.objects.create(
            username='pat',
            password='password',
            email='pat@rat.com',
            first_name='Pat',
            last_name='Smith',
            profile_is_public=True,
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
        self.assert_blocks_reserved(1, self.block1)

        reservation = BlockfaceReservation.objects.get(blockface=self.block1)
        self.assertEqual(self.user.pk, reservation.user_id)

    def test_already_reserved(self):
        self.assert_blocks_reserved(1, self.block1)

        reservation = BlockfaceReservation.objects.get(blockface=self.block1)
        self.assertEqual(self.user.pk, reservation.user_id)

        self.assert_blocks_reserved(1, self.block1, self.block2)

        self.assertEqual(1, BlockfaceReservation.objects
                         .filter(blockface=self.block1).count())
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
        Territory.objects.create(group=group, blockface=self.block1)

        self.assert_blocks_reserved(0, self.block1)

        TrustedMapper.objects.create(group=group, user=self.user)

        self.assert_blocks_reserved(01, self.block1)
