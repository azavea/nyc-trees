# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from functools import partial

from django.core import mail
from django.http import HttpResponseForbidden

from apps.core.test_utils import make_request, make_event

from apps.users.tests import UsersTestCase

from apps.event.models import Event, EventRegistration
from apps.event.views import (events_list_page,
                              event_email,
                              register_for_event,
                              event_check_in_page,
                              check_in_user_to_event,
                              increase_rsvp_limit)


class EventTestCase(UsersTestCase):
    def setUp(self):
        super(EventTestCase, self).setUp()
        self.event = make_event(self.group)


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
        }, self.other_user, 'POST', group=self.group)

        context = event_email(request, self.event.slug)

        self.assertEqual(mail.outbox[0].subject, "Come to the event")
        self.assertTrue(context['message_sent'])
        self.assertEqual(self.event, context['event'])
        self.assertEqual(self.group, context['group'])

        # Clear the test inbox
        mail.outbox = []


class CheckinEventTest(EventTestCase):
    def _assert_num_checkins(self, expected_amount):
        request = make_request(user=self.user, group=self.group)
        context = event_check_in_page(request, self.event.slug)
        self.assertEqual(self.event, context['event'])
        self.assertEqual(self.group, context['group'])

        checkins = sum(1 if did_attend else 0
                       for user, did_attend in context['users'])
        self.assertEqual(expected_amount, checkins)

    def test_checkin_checkout(self):
        self._assert_num_checkins(0)
        request = partial(make_request, user=self.user, group=self.group)

        # Checkin (should fail because user has not RSVPed yet)
        context = check_in_user_to_event(request(method='POST'),
                                         self.event.slug,
                                         self.user.username)
        self.assertTrue(isinstance(context, HttpResponseForbidden))

        # RSVP
        register_for_event(request(method='POST'), self.event.slug)

        # Checkin again (should succeed this time)
        check_in_user_to_event(request(method='POST'),
                               self.event.slug,
                               self.user.username)
        self._assert_num_checkins(1)

        # Un-Checkin
        check_in_user_to_event(request(method='DELETE'),
                               self.event.slug,
                               self.user.username)
        self._assert_num_checkins(0)

    def test_rsvp_limit_increase(self):
        request = make_request(user=self.user, group=self.group)

        self.event.max_attendees = 0
        self.event.save()

        self.event = Event.objects.get(id=self.event.id)
        self.assertEqual(0, self.event.max_attendees)

        context = increase_rsvp_limit(request, self.event.slug)
        self.event = Event.objects.get(id=self.event.id)
        self.assertEqual(5, context['max_attendees'])
        self.assertEqual(5, self.event.max_attendees)

        context = increase_rsvp_limit(request, self.event.slug)
        self.event = Event.objects.get(id=self.event.id)
        self.assertEqual(10, context['max_attendees'])
        self.assertEqual(10, self.event.max_attendees)

        context = increase_rsvp_limit(request, self.event.slug)
        self.event = Event.objects.get(id=self.event.id)
        self.assertEqual(15, context['max_attendees'])
        self.assertEqual(15, self.event.max_attendees)
