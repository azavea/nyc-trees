# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.gis.geos import Point
from django.core import mail

from django.utils.timezone import now
from apps.core.test_utils import make_request

from apps.users.tests import UsersTestCase

from apps.event.models import Event, EventRegistration
from apps.event.views import events_list_page, event_email


class EventTestCase(UsersTestCase):
    def setUp(self):
        super(EventTestCase, self).setUp()
        self.event = Event.objects.create(group=self.group,
                                          title="The event",
                                          contact_email="a@b.com",
                                          address="123 Main St",
                                          location=Point(0, 0),
                                          max_attendees=100,
                                          begins_at=now(),
                                          ends_at=now())


class EventListTest(EventTestCase):
    def test_following_user(self):
        request = make_request(user=self.user)
        ctx = events_list_page(request)
        self.assertEqual(len(ctx['all_events']['event_infos']), 1)
        self.assertEqual(len(ctx['immediate_events']['event_infos']), 1)
        self.assertFalse(
            ctx['immediate_events']['event_infos'][0]['user_is_registered'])

    def test_following_user_registered(self):
        EventRegistration.objects.create(user=self.user,
                                         event=self.event)
        request = make_request(user=self.user)
        ctx = events_list_page(request)
        self.assertEqual(len(ctx['all_events']['event_infos']), 1)
        self.assertEqual(len(ctx['immediate_events']['event_infos']), 1)
        self.assertTrue(
            ctx['immediate_events']['event_infos'][0]['user_is_registered'])

    def test_other_user(self):
        request = make_request(user=self.other_user)
        ctx = events_list_page(request)
        self.assertEqual(len(ctx['all_events']['event_infos']), 1)
        self.assertEqual(len(ctx['immediate_events']['event_infos']), 0)
        self.assertFalse(
            ctx['all_events']['event_infos'][0]['user_is_registered'])


class EventEmailTest(EventTestCase):
    def test_sending_email(self):
        reg = EventRegistration(event=self.event, user=self.user)
        reg.clean_and_save()

        request = make_request({
            'subject': 'Come to the event',
            'body': "It's happening now!"
        }, self.other_user, 'POST')

        context = event_email(request, self.group.slug, self.event.slug)

        self.assertEqual(mail.outbox[0].subject, "Come to the event")
        self.assertTrue(context['message_sent'])
        self.assertEqual(self.event, context['event'])
        self.assertEqual(self.group, context['group'])

        # Clear the test inbox
        mail.outbox = []
