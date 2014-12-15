# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.gis.geos import Point

from django.utils.timezone import now
from apps.core.test_utils import make_request

from apps.users.tests import UsersTestCase

from apps.event.models import Event, EventRegistration
from apps.event.views import events_list_page


class EventListTest(UsersTestCase):
    def setUp(self):
        super(EventListTest, self).setUp()
        self.event = Event.objects.create(group=self.group,
                                          title="The event",
                                          contact_email="a@b.com",
                                          address="123 Main St",
                                          location=Point(0, 0),
                                          max_attendees=100,
                                          begins_at=now(),
                                          ends_at=now())

    def test_following_user(self):
        request = make_request(user=self.user)
        ctx = events_list_page(request)
        self.assertEqual(len(ctx['non_followed_events']), 0)
        self.assertFalse(ctx['followed_events'][0]['user_is_registered'])

    def test_following_user_registered(self):
        EventRegistration.objects.create(user=self.user,
                                         event=self.event)
        request = make_request(user=self.user)
        ctx = events_list_page(request)
        self.assertEqual(len(ctx['non_followed_events']), 0)
        self.assertTrue(ctx['followed_events'][0]['user_is_registered'])

    def test_other_user(self):
        request = make_request(user=self.other_user)
        ctx = events_list_page(request)
        self.assertEqual(len(ctx['followed_events']), 0)
        self.assertFalse(ctx['non_followed_events'][0]['user_is_registered'])
